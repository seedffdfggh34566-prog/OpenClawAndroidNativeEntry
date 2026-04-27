from __future__ import annotations

from collections.abc import Callable
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from backend.api.database import get_session_factory
from backend.sales_workspace.patches import apply_workspace_patch
from backend.sales_workspace.draft_reviews import (
    DraftReviewNotFound,
    WorkspacePatchDraftApplyResult,
    WorkspacePatchDraftPreview,
    WorkspacePatchDraftReview,
    WorkspacePatchDraftReviewDecision,
)
from backend.sales_workspace.schemas import SalesWorkspace, WorkspacePatch
from backend.sales_workspace.store import WorkspaceNotFound

metadata = sa.MetaData()

sales_workspaces = sa.Table(
    "sales_workspaces",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("workspace_key", sa.Text(), nullable=False),
    sa.Column("owner_id", sa.Text(), nullable=True),
    sa.Column("tenant_id", sa.Text(), nullable=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("goal", sa.Text(), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("workspace_version", sa.Integer(), nullable=False),
    sa.Column("current_product_profile_revision_id", sa.Text(), nullable=True),
    sa.Column("current_lead_direction_id", sa.Text(), nullable=True),
    sa.Column("latest_research_round_id", sa.Text(), nullable=True),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_by", sa.Text(), nullable=True),
    sa.Column("updated_by", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_product_profile_revisions = sa.Table(
    "sales_workspace_product_profile_revisions",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("revision_id", sa.Text(), primary_key=True),
    sa.Column("version", sa.Integer(), nullable=False),
    sa.Column("product_name", sa.Text(), nullable=False),
    sa.Column("one_liner", sa.Text(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_lead_directions = sa.Table(
    "sales_workspace_lead_directions",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("direction_id", sa.Text(), primary_key=True),
    sa.Column("version", sa.Integer(), nullable=False),
    sa.Column("change_reason", sa.Text(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_lead_candidates = sa.Table(
    "sales_workspace_lead_candidates",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("candidate_id", sa.Text(), primary_key=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("industry", sa.Text(), nullable=False),
    sa.Column("region", sa.Text(), nullable=False),
    sa.Column("company_size", sa.Text(), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_research_sources = sa.Table(
    "sales_workspace_research_sources",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("source_id", sa.Text(), primary_key=True),
    sa.Column("round_id", sa.Text(), nullable=False),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("url", sa.Text(), nullable=True),
    sa.Column("source_type", sa.Text(), nullable=False),
    sa.Column("reliability", sa.Text(), nullable=False),
    sa.Column("excerpt", sa.Text(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_research_observations = sa.Table(
    "sales_workspace_research_observations",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("observation_id", sa.Text(), primary_key=True),
    sa.Column("candidate_id", sa.Text(), nullable=False),
    sa.Column("source_id", sa.Text(), nullable=False),
    sa.Column("round_id", sa.Text(), nullable=False),
    sa.Column("signal_type", sa.Text(), nullable=False),
    sa.Column("polarity", sa.Text(), nullable=False),
    sa.Column("strength", sa.Integer(), nullable=False),
    sa.Column("summary", sa.Text(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_patch_commits = sa.Table(
    "sales_workspace_patch_commits",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("commit_id", sa.Text(), primary_key=True),
    sa.Column("patch_id", sa.Text(), nullable=False),
    sa.Column("base_workspace_version", sa.Integer(), nullable=False),
    sa.Column("resulting_workspace_version", sa.Integer(), nullable=False),
    sa.Column("author", sa.Text(), nullable=False),
    sa.Column("message", sa.Text(), nullable=False),
    sa.Column("operation_count", sa.Integer(), nullable=False),
    sa.Column("changed_object_refs", sa.JSON(), nullable=False),
    sa.Column("patch_json", sa.JSON(), nullable=False),
    sa.Column("commit_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_draft_reviews = sa.Table(
    "sales_workspace_draft_reviews",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("draft_review_id", sa.Text(), primary_key=True),
    sa.Column("draft_id", sa.Text(), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("base_workspace_version", sa.Integer(), nullable=False),
    sa.Column("instruction", sa.Text(), nullable=False),
    sa.Column("created_by", sa.Text(), nullable=False),
    sa.Column("reviewed_by", sa.Text(), nullable=True),
    sa.Column("applied_commit_id", sa.Text(), nullable=True),
    sa.Column("failure_code", sa.Text(), nullable=True),
    sa.Column("failure_reason", sa.Text(), nullable=True),
    sa.Column("draft_json", sa.JSON(), nullable=False),
    sa.Column("preview_json", sa.JSON(), nullable=False),
    sa.Column("review_json", sa.JSON(), nullable=True),
    sa.Column("apply_result_json", sa.JSON(), nullable=True),
    sa.Column("runtime_metadata", sa.JSON(), nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_draft_review_events = sa.Table(
    "sales_workspace_draft_review_events",
    metadata,
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("draft_review_id", sa.Text(), nullable=False),
    sa.Column("event_id", sa.Text(), primary_key=True),
    sa.Column("event_type", sa.Text(), nullable=False),
    sa.Column("from_status", sa.Text(), nullable=True),
    sa.Column("to_status", sa.Text(), nullable=False),
    sa.Column("actor_type", sa.Text(), nullable=False),
    sa.Column("actor_id", sa.Text(), nullable=True),
    sa.Column("reason", sa.Text(), nullable=False),
    sa.Column("event_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)


class PostgresWorkspaceStore:
    """SQLAlchemy-backed Sales Workspace store for the Postgres persistence path."""

    def __init__(self, session_factory: sessionmaker[Session] | Callable[[], Session] | None = None) -> None:
        self._session_factory = session_factory or get_session_factory()

    def create_workspace(
        self,
        *,
        workspace_id: str,
        name: str,
        goal: str = "",
        owner_id: str = "local_user",
        workspace_key: str = "local_default",
    ) -> SalesWorkspace:
        workspace = SalesWorkspace(
            id=workspace_id,
            workspace_key=workspace_key,
            owner_id=owner_id,
            name=name,
            goal=goal,
        )
        self.save(workspace)
        return workspace

    def get(self, workspace_id: str) -> SalesWorkspace:
        with self._session_factory() as session:
            return self._get_workspace(session, workspace_id)

    def save(self, workspace: SalesWorkspace) -> None:
        with self._session_factory() as session:
            with session.begin():
                self._upsert_workspace(session, workspace)
                self._replace_workspace_objects(session, workspace)

    def apply_patch(self, patch: WorkspacePatch) -> SalesWorkspace:
        with self._session_factory() as session:
            with session.begin():
                workspace = self._get_workspace(session, patch.workspace_id, for_update=True)
                updated = apply_workspace_patch(workspace, patch)
                self._upsert_workspace(session, updated)
                self._replace_workspace_objects(session, updated)
                self._insert_patch_commit(session, updated, patch)
                return updated

    def _get_workspace(self, session: Session, workspace_id: str, *, for_update: bool = False) -> SalesWorkspace:
        statement = sa.select(sales_workspaces.c.payload_json).where(sales_workspaces.c.workspace_id == workspace_id)
        if for_update:
            statement = statement.with_for_update()
        row = session.execute(statement).first()
        if row is None:
            raise WorkspaceNotFound(workspace_id)
        return SalesWorkspace.model_validate(row.payload_json)

    def _upsert_workspace(self, session: Session, workspace: SalesWorkspace) -> None:
        payload = _json(workspace)
        values = {
            "workspace_id": workspace.id,
            "workspace_key": workspace.workspace_key,
            "owner_id": workspace.owner_id,
            "tenant_id": None,
            "name": workspace.name,
            "goal": workspace.goal,
            "status": workspace.status,
            "workspace_version": workspace.workspace_version,
            "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
            "current_lead_direction_id": workspace.current_lead_direction_version_id,
            "latest_research_round_id": workspace.latest_research_round_id,
            "payload_json": payload,
            "created_by": None,
            "updated_by": None,
            "created_at": workspace.created_at,
            "updated_at": workspace.updated_at,
        }
        updated = session.execute(
            sales_workspaces.update()
            .where(sales_workspaces.c.workspace_id == workspace.id)
            .values(**values)
        ).rowcount
        if not updated:
            session.execute(sales_workspaces.insert().values(**values))

    def _replace_workspace_objects(self, session: Session, workspace: SalesWorkspace) -> None:
        workspace_filter = {"workspace_id": workspace.id}
        for table in [
            sales_workspace_research_observations,
            sales_workspace_research_sources,
            sales_workspace_lead_candidates,
            sales_workspace_lead_directions,
            sales_workspace_product_profile_revisions,
        ]:
            session.execute(table.delete().where(table.c.workspace_id == workspace.id))

        if workspace.product_profile_revisions:
            session.execute(
                sales_workspace_product_profile_revisions.insert(),
                [
                    {
                        **workspace_filter,
                        "revision_id": revision.id,
                        "version": revision.version,
                        "product_name": revision.product_name,
                        "one_liner": revision.one_liner,
                        "payload_json": _json(revision),
                        "created_at": revision.created_at,
                    }
                    for revision in workspace.product_profile_revisions.values()
                ],
            )

        if workspace.lead_direction_versions:
            session.execute(
                sales_workspace_lead_directions.insert(),
                [
                    {
                        **workspace_filter,
                        "direction_id": direction.id,
                        "version": direction.version,
                        "change_reason": direction.change_reason,
                        "payload_json": _json(direction),
                        "created_at": direction.created_at,
                    }
                    for direction in workspace.lead_direction_versions.values()
                ],
            )

        if workspace.company_candidates:
            session.execute(
                sales_workspace_lead_candidates.insert(),
                [
                    {
                        **workspace_filter,
                        "candidate_id": candidate.id,
                        "name": candidate.name,
                        "industry": candidate.industry,
                        "region": candidate.region,
                        "company_size": candidate.company_size,
                        "status": candidate.status,
                        "payload_json": _json(candidate),
                        "created_at": candidate.created_at,
                        "updated_at": candidate.updated_at,
                    }
                    for candidate in workspace.company_candidates.values()
                ],
            )

        if workspace.research_sources:
            session.execute(
                sales_workspace_research_sources.insert(),
                [
                    {
                        **workspace_filter,
                        "source_id": source.id,
                        "round_id": source.round_id,
                        "title": source.title,
                        "url": source.url,
                        "source_type": source.source_type,
                        "reliability": source.reliability,
                        "excerpt": source.excerpt,
                        "payload_json": _json(source),
                        "collected_at": source.collected_at,
                    }
                    for source in workspace.research_sources.values()
                ],
            )

        if workspace.candidate_observations:
            session.execute(
                sales_workspace_research_observations.insert(),
                [
                    {
                        **workspace_filter,
                        "observation_id": observation.id,
                        "candidate_id": observation.candidate_id,
                        "source_id": observation.source_id,
                        "round_id": observation.round_id,
                        "signal_type": observation.signal_type,
                        "polarity": observation.polarity,
                        "strength": observation.strength,
                        "summary": observation.summary,
                        "payload_json": _json(observation),
                        "created_at": observation.created_at,
                    }
                    for observation in workspace.candidate_observations.values()
                ],
            )

    def _insert_patch_commit(self, session: Session, workspace: SalesWorkspace, patch: WorkspacePatch) -> None:
        commit = workspace.commits[-1]
        session.execute(
            sales_workspace_patch_commits.insert().values(
                workspace_id=workspace.id,
                commit_id=commit.id,
                patch_id=patch.id,
                base_workspace_version=patch.base_workspace_version,
                resulting_workspace_version=commit.workspace_version,
                author=patch.author,
                message=patch.message,
                operation_count=len(patch.operations),
                changed_object_refs=commit.changed_object_refs,
                patch_json=_json(patch),
                commit_json=_json(commit),
                created_at=commit.created_at,
            )
        )


class PostgresDraftReviewStore:
    """SQLAlchemy-backed Draft Review store for the Postgres persistence path."""

    def __init__(self, session_factory: sessionmaker[Session] | Callable[[], Session] | None = None) -> None:
        self._session_factory = session_factory or get_session_factory()

    def save(self, draft_review: WorkspacePatchDraftReview) -> None:
        with self._session_factory() as session:
            with session.begin():
                previous = self._get_review_row(session, draft_review.workspace_id, draft_review.id, for_update=True)
                self._upsert_review(session, draft_review)
                self._append_lifecycle_events(session, draft_review, previous)

    def get(self, workspace_id: str, draft_review_id: str) -> WorkspacePatchDraftReview:
        with self._session_factory() as session:
            row = self._get_review_row(session, workspace_id, draft_review_id)
            if row is None:
                raise DraftReviewNotFound(draft_review_id)
            return self._review_from_row(row)

    def _get_review_row(
        self,
        session: Session,
        workspace_id: str,
        draft_review_id: str,
        *,
        for_update: bool = False,
    ) -> dict[str, Any] | None:
        statement = sa.select(sales_workspace_draft_reviews).where(
            sales_workspace_draft_reviews.c.workspace_id == workspace_id,
            sales_workspace_draft_reviews.c.draft_review_id == draft_review_id,
        )
        if for_update:
            statement = statement.with_for_update()
        row = session.execute(statement).mappings().first()
        return dict(row) if row is not None else None

    def _upsert_review(self, session: Session, draft_review: WorkspacePatchDraftReview) -> None:
        apply_result = draft_review.apply_result
        values = {
            "workspace_id": draft_review.workspace_id,
            "draft_review_id": draft_review.id,
            "draft_id": draft_review.draft.id,
            "status": draft_review.status,
            "base_workspace_version": draft_review.base_workspace_version,
            "instruction": draft_review.instruction,
            "created_by": draft_review.created_by,
            "reviewed_by": draft_review.review.reviewed_by if draft_review.review else None,
            "applied_commit_id": _applied_commit_id(draft_review),
            "failure_code": apply_result.error_code if apply_result else None,
            "failure_reason": apply_result.error_message if apply_result else None,
            "draft_json": _json(draft_review.draft),
            "preview_json": _json(draft_review.preview),
            "review_json": _optional_json(draft_review.review),
            "apply_result_json": _optional_json(apply_result),
            "runtime_metadata": draft_review.runtime_metadata,
            "expires_at": draft_review.expires_at,
            "created_at": draft_review.created_at,
            "updated_at": draft_review.updated_at,
        }
        updated = session.execute(
            sales_workspace_draft_reviews.update()
            .where(
                sales_workspace_draft_reviews.c.workspace_id == draft_review.workspace_id,
                sales_workspace_draft_reviews.c.draft_review_id == draft_review.id,
            )
            .values(**values)
        ).rowcount
        if not updated:
            session.execute(sales_workspace_draft_reviews.insert().values(**values))

    def _append_lifecycle_events(
        self,
        session: Session,
        draft_review: WorkspacePatchDraftReview,
        previous: dict[str, Any] | None,
    ) -> None:
        previous_status = previous["status"] if previous else None
        events: list[str] = []

        if previous is None:
            events.append("created")
        elif previous_status != draft_review.status:
            if draft_review.status == "reviewed":
                events.append("reviewed")
            elif draft_review.status == "rejected":
                events.append("rejected")
            elif draft_review.status == "applied":
                events.append("applied")
            elif draft_review.status == "expired":
                events.append("expired")

        previous_apply_result = previous["apply_result_json"] if previous else None
        current_apply_result = _optional_json(draft_review.apply_result)
        if (
            draft_review.apply_result is not None
            and draft_review.apply_result.status == "failed"
            and current_apply_result != previous_apply_result
        ):
            events.append("apply_failed")

        for event_type in events:
            self._insert_event(
                session,
                draft_review,
                event_type=event_type,
                from_status=previous_status,
                to_status=draft_review.status,
            )

    def _insert_event(
        self,
        session: Session,
        draft_review: WorkspacePatchDraftReview,
        *,
        event_type: str,
        from_status: str | None,
        to_status: str,
    ) -> None:
        next_index = (
            session.execute(
                sa.select(sa.func.count())
                .select_from(sales_workspace_draft_review_events)
                .where(
                    sales_workspace_draft_review_events.c.workspace_id == draft_review.workspace_id,
                    sales_workspace_draft_review_events.c.draft_review_id == draft_review.id,
                )
            ).scalar_one()
            + 1
        )
        actor_type, actor_id = _event_actor(draft_review, event_type)
        reason = _event_reason(draft_review, event_type)
        session.execute(
            sales_workspace_draft_review_events.insert().values(
                workspace_id=draft_review.workspace_id,
                draft_review_id=draft_review.id,
                event_id=f"{draft_review.id}_event_{next_index:04d}",
                event_type=event_type,
                from_status=from_status,
                to_status=to_status,
                actor_type=actor_type,
                actor_id=actor_id,
                reason=reason,
                event_json={
                    "draft_review_id": draft_review.id,
                    "event_type": event_type,
                    "from_status": from_status,
                    "to_status": to_status,
                    "review": _optional_json(draft_review.review),
                    "apply_result": _optional_json(draft_review.apply_result),
                },
                created_at=draft_review.updated_at,
            )
        )

    def _review_from_row(self, row: dict[str, Any]) -> WorkspacePatchDraftReview:
        return WorkspacePatchDraftReview(
            id=row["draft_review_id"],
            workspace_id=row["workspace_id"],
            draft=row["draft_json"],
            status=row["status"],
            base_workspace_version=row["base_workspace_version"],
            created_by=row["created_by"],
            created_at=row["created_at"],
            instruction=row["instruction"],
            runtime_metadata=row["runtime_metadata"],
            preview=WorkspacePatchDraftPreview.model_validate(row["preview_json"]),
            review=WorkspacePatchDraftReviewDecision.model_validate(row["review_json"])
            if row["review_json"] is not None
            else None,
            apply_result=WorkspacePatchDraftApplyResult.model_validate(row["apply_result_json"])
            if row["apply_result_json"] is not None
            else None,
            expires_at=row["expires_at"],
            updated_at=row["updated_at"],
        )


def _json(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")


def _optional_json(model: Any | None) -> dict[str, Any] | None:
    return model.model_dump(mode="json") if model is not None else None


def _applied_commit_id(draft_review: WorkspacePatchDraftReview) -> str | None:
    apply_result = draft_review.apply_result
    if apply_result is None or apply_result.status != "applied" or apply_result.workspace_version is None:
        return None
    return f"commit_v{apply_result.workspace_version}"


def _event_actor(draft_review: WorkspacePatchDraftReview, event_type: str) -> tuple[str, str | None]:
    if event_type in {"reviewed", "rejected"} and draft_review.review is not None:
        return "human", draft_review.review.reviewed_by
    if event_type == "created":
        return "runtime", draft_review.created_by
    return "backend", None


def _event_reason(draft_review: WorkspacePatchDraftReview, event_type: str) -> str:
    if event_type in {"reviewed", "rejected"} and draft_review.review is not None:
        return draft_review.review.comment
    if event_type == "apply_failed" and draft_review.apply_result is not None:
        return draft_review.apply_result.error_message or draft_review.apply_result.error_code or ""
    if event_type == "created":
        return draft_review.instruction
    return ""
