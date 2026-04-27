from __future__ import annotations

from collections.abc import Callable
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from backend.api.database import get_session_factory
from backend.sales_workspace.patches import apply_workspace_patch
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


def _json(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")
