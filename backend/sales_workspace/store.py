from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote

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

    def list_workspaces(self) -> list[SalesWorkspace]:
        return sorted(
            self._workspaces.values(),
            key=lambda workspace: workspace.updated_at,
            reverse=True,
        )

    def apply_patch(self, patch: WorkspacePatch) -> SalesWorkspace:
        workspace = self.get(patch.workspace_id)
        updated = apply_workspace_patch(workspace, patch)
        self.save(updated)
        return updated


class JsonFileWorkspaceStore(InMemoryWorkspaceStore):
    def __init__(self, store_dir: str | Path) -> None:
        super().__init__()
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def get(self, workspace_id: str) -> SalesWorkspace:
        try:
            return super().get(workspace_id)
        except WorkspaceNotFound:
            path = self._workspace_path(workspace_id)
            if not path.exists():
                raise
            workspace = load_workspace_json(path)
            self._workspaces[workspace.id] = workspace
            return workspace

    def save(self, workspace: SalesWorkspace) -> None:
        self._workspaces[workspace.id] = workspace
        save_workspace_json(self._workspace_path(workspace.id), workspace)

    def list_workspaces(self) -> list[SalesWorkspace]:
        file_workspaces = {}
        for path in self.store_dir.glob("*.json"):
            if not path.is_file():
                continue
            workspace = load_workspace_json(path)
            file_workspaces[workspace.id] = workspace

        merged = {**file_workspaces, **self._workspaces}
        self._workspaces.update(merged)
        return sorted(
            merged.values(),
            key=lambda workspace: workspace.updated_at,
            reverse=True,
        )

    def _workspace_path(self, workspace_id: str) -> Path:
        filename = f"{quote(workspace_id, safe='')}.json"
        return self.store_dir / filename


def save_workspace_json(path: str | Path, workspace: SalesWorkspace) -> None:
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
        tmp_file.write(workspace.model_dump_json(indent=2))
        tmp_path = Path(tmp_file.name)
    tmp_path.replace(output_path)


def load_workspace_json(path: str | Path) -> SalesWorkspace:
    input_path = Path(path)
    return SalesWorkspace.model_validate(json.loads(input_path.read_text(encoding="utf-8")))
