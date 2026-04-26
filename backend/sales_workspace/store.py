from __future__ import annotations

import json
from pathlib import Path

from backend.sales_workspace.patches import apply_workspace_patch
from backend.sales_workspace.schemas import SalesWorkspace, WorkspacePatch


class WorkspaceNotFound(KeyError):
    pass


class InMemoryWorkspaceStore:
    def __init__(self) -> None:
        self._workspaces: dict[str, SalesWorkspace] = {}

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
        self._workspaces[workspace.id] = workspace
        return workspace

    def save(self, workspace: SalesWorkspace) -> None:
        self._workspaces[workspace.id] = workspace

    def get(self, workspace_id: str) -> SalesWorkspace:
        try:
            return self._workspaces[workspace_id]
        except KeyError as exc:
            raise WorkspaceNotFound(workspace_id) from exc

    def apply_patch(self, patch: WorkspacePatch) -> SalesWorkspace:
        workspace = self.get(patch.workspace_id)
        updated = apply_workspace_patch(workspace, patch)
        self.save(updated)
        return updated


def save_workspace_json(path: str | Path, workspace: SalesWorkspace) -> None:
    output_path = Path(path)
    output_path.write_text(workspace.model_dump_json(indent=2), encoding="utf-8")


def load_workspace_json(path: str | Path) -> SalesWorkspace:
    input_path = Path(path)
    return SalesWorkspace.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
