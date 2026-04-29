from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, Field

from backend.runtime.sales_workspace_patchdraft import WorkspacePatchDraft
from backend.sales_workspace.schemas import CandidateRankingBoard, WorkspacePatch, utc_now


DraftReviewStatus = Literal["previewed", "reviewed", "applied", "rejected", "expired"]
DraftReviewDecision = Literal["accept", "reject"]


class DraftReviewModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorkspacePatchDraftPreview(DraftReviewModel):
    materialized_patch: WorkspacePatch
    preview_workspace_version: int
    preview_ranking_board: CandidateRankingBoard | None = None
    would_mutate: bool = False
    generated_at: datetime = Field(default_factory=utc_now)


class WorkspacePatchDraftReviewDecision(DraftReviewModel):
    decision: DraftReviewDecision
    reviewed_by: str = "android_demo_user"
    comment: str = ""
    client: str = "api"
    reviewed_at: datetime = Field(default_factory=utc_now)


class WorkspacePatchDraftApplyResult(DraftReviewModel):
    status: Literal["applied", "failed"]
    materialized_patch_id: str | None = None
    workspace_version: int | None = None
    ranking_impact_summary: dict[str, str | int | None] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    applied_at: datetime | None = None
    failed_at: datetime | None = None


class WorkspacePatchDraftReview(DraftReviewModel):
    id: str
    workspace_id: str
    draft: WorkspacePatchDraft
    status: DraftReviewStatus = "previewed"
    base_workspace_version: int
    created_by: str = "runtime_patchdraft_prototype"
    created_at: datetime = Field(default_factory=utc_now)
    instruction: str = ""
    runtime_metadata: dict[str, object] = Field(default_factory=dict)
    preview: WorkspacePatchDraftPreview
    review: WorkspacePatchDraftReviewDecision | None = None
    apply_result: WorkspacePatchDraftApplyResult | None = None
    expires_at: datetime | None = None
    updated_at: datetime = Field(default_factory=utc_now)


class DraftReviewNotFound(KeyError):
    pass


def draft_review_id_for_draft(draft_id: str) -> str:
    if draft_id.startswith("draft_"):
        return draft_id.replace("draft_", "draft_review_", 1)
    return f"draft_review_{draft_id}"


class InMemoryDraftReviewStore:
    def __init__(self) -> None:
        self._draft_reviews: dict[tuple[str, str], WorkspacePatchDraftReview] = {}

    def save(self, draft_review: WorkspacePatchDraftReview) -> None:
        self._draft_reviews[(draft_review.workspace_id, draft_review.id)] = draft_review

    def get(self, workspace_id: str, draft_review_id: str) -> WorkspacePatchDraftReview:
        try:
            return self._draft_reviews[(workspace_id, draft_review_id)]
        except KeyError as exc:
            raise DraftReviewNotFound(draft_review_id) from exc

    def list_draft_reviews(
        self,
        workspace_id: str,
        status: DraftReviewStatus | None = None,
    ) -> list[WorkspacePatchDraftReview]:
        return sorted(
            [
                draft_review
                for (stored_workspace_id, _), draft_review in self._draft_reviews.items()
                if stored_workspace_id == workspace_id and (status is None or draft_review.status == status)
            ],
            key=lambda draft_review: draft_review.updated_at,
            reverse=True,
        )


class JsonFileDraftReviewStore(InMemoryDraftReviewStore):
    def __init__(self, store_dir: str | Path) -> None:
        super().__init__()
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def save(self, draft_review: WorkspacePatchDraftReview) -> None:
        super().save(draft_review)
        save_draft_review_json(self._draft_review_path(draft_review.workspace_id, draft_review.id), draft_review)

    def get(self, workspace_id: str, draft_review_id: str) -> WorkspacePatchDraftReview:
        try:
            return super().get(workspace_id, draft_review_id)
        except DraftReviewNotFound:
            path = self._draft_review_path(workspace_id, draft_review_id)
            if not path.exists():
                raise
            draft_review = load_draft_review_json(path)
            self._draft_reviews[(draft_review.workspace_id, draft_review.id)] = draft_review
            return draft_review

    def list_draft_reviews(
        self,
        workspace_id: str,
        status: DraftReviewStatus | None = None,
    ) -> list[WorkspacePatchDraftReview]:
        file_reviews = {}
        workspace_dir = self.store_dir / "draft_reviews" / quote(workspace_id, safe="")
        if workspace_dir.exists():
            for path in workspace_dir.glob("*.json"):
                if not path.is_file():
                    continue
                draft_review = load_draft_review_json(path)
                file_reviews[(draft_review.workspace_id, draft_review.id)] = draft_review

        merged = {**file_reviews, **self._draft_reviews}
        self._draft_reviews.update(merged)
        return sorted(
            [
                draft_review
                for (stored_workspace_id, _), draft_review in merged.items()
                if stored_workspace_id == workspace_id and (status is None or draft_review.status == status)
            ],
            key=lambda draft_review: draft_review.updated_at,
            reverse=True,
        )

    def _draft_review_path(self, workspace_id: str, draft_review_id: str) -> Path:
        workspace_dir = quote(workspace_id, safe="")
        filename = f"{quote(draft_review_id, safe='')}.json"
        return self.store_dir / "draft_reviews" / workspace_dir / filename


def save_draft_review_json(path: str | Path, draft_review: WorkspacePatchDraftReview) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as tmp_file:
        tmp_file.write(draft_review.model_dump_json(indent=2))
        tmp_path = Path(tmp_file.name)
    tmp_path.replace(output_path)


def load_draft_review_json(path: str | Path) -> WorkspacePatchDraftReview:
    input_path = Path(path)
    return WorkspacePatchDraftReview.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
