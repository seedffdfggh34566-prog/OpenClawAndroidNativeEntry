from __future__ import annotations

from pathlib import Path
from threading import Lock

from backend.runtime.v3_sandbox.schemas import V3SandboxSession


class V3SandboxSessionNotFound(KeyError):
    pass


class InMemoryV3SandboxStore:
    def __init__(self) -> None:
        self._sessions: dict[str, V3SandboxSession] = {}
        self._lock = Lock()

    def create_session(self, session: V3SandboxSession) -> V3SandboxSession:
        with self._lock:
            self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> V3SandboxSession:
        with self._lock:
            try:
                return self._sessions[session_id].model_copy(deep=True)
            except KeyError as exc:
                raise V3SandboxSessionNotFound(session_id) from exc

    def save_session(self, session: V3SandboxSession) -> V3SandboxSession:
        with self._lock:
            self._sessions[session.id] = session.model_copy(deep=True)
        return session

    def list_sessions(self) -> list[V3SandboxSession]:
        with self._lock:
            return [session.model_copy(deep=True) for session in self._sessions.values()]


class JsonFileV3SandboxStore(InMemoryV3SandboxStore):
    def __init__(self, store_dir: str | Path) -> None:
        super().__init__()
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, session: V3SandboxSession) -> V3SandboxSession:
        saved = super().create_session(session)
        self._write_session(saved)
        return saved

    def get_session(self, session_id: str) -> V3SandboxSession:
        try:
            return super().get_session(session_id)
        except V3SandboxSessionNotFound:
            path = self._session_path(session_id)
            if not path.exists():
                raise
            session = V3SandboxSession.model_validate_json(path.read_text(encoding="utf-8"))
            super().save_session(session)
            return session

    def save_session(self, session: V3SandboxSession) -> V3SandboxSession:
        saved = super().save_session(session)
        self._write_session(saved)
        return saved

    def list_sessions(self) -> list[V3SandboxSession]:
        for path in sorted(self.store_dir.glob("*.json")):
            session = V3SandboxSession.model_validate_json(path.read_text(encoding="utf-8"))
            super().save_session(session)
        return super().list_sessions()

    def _write_session(self, session: V3SandboxSession) -> None:
        self._session_path(session.id).write_text(
            session.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def _session_path(self, session_id: str) -> Path:
        safe_id = "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in session_id)
        return self.store_dir / f"{safe_id}.json"
