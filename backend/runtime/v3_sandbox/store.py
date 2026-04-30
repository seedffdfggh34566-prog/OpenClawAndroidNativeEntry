from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from backend.api.database import get_session_factory
from backend.api.models import (
    V3SandboxActionEventRecord,
    V3SandboxMemoryItemRecord,
    V3SandboxMemoryTransitionEventRecord,
    V3SandboxMessageRecord,
    V3SandboxSessionRecord,
    V3SandboxTraceEventRecord,
)
from backend.runtime.v3_sandbox.schemas import AgentAction, MemoryItem, V3SandboxSession, utc_now


class V3SandboxSessionNotFound(KeyError):
    pass


class V3SandboxStoreConfigError(ValueError):
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


class DatabaseV3SandboxStore:
    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        self._session_factory = session_factory or get_session_factory()

    def create_session(self, session: V3SandboxSession) -> V3SandboxSession:
        return self.save_session(session)

    def get_session(self, session_id: str) -> V3SandboxSession:
        with self._session_factory() as db:
            record = db.get(V3SandboxSessionRecord, session_id)
            if record is None:
                raise V3SandboxSessionNotFound(session_id)
            return V3SandboxSession.model_validate(record.payload_json)

    def save_session(self, session: V3SandboxSession) -> V3SandboxSession:
        snapshot = session.model_copy(deep=True)
        with self._session_factory() as db:
            db.merge(
                V3SandboxSessionRecord(
                    session_id=snapshot.id,
                    title=snapshot.title,
                    payload_json=snapshot.model_dump(mode="json"),
                    created_at=snapshot.created_at,
                    updated_at=snapshot.updated_at,
                )
            )
            self._replace_normalized_rows(db, snapshot)
            db.commit()
        return snapshot

    def list_sessions(self) -> list[V3SandboxSession]:
        with self._session_factory() as db:
            records = db.scalars(select(V3SandboxSessionRecord).order_by(V3SandboxSessionRecord.updated_at)).all()
            return [V3SandboxSession.model_validate(record.payload_json) for record in records]

    def memory_transitions(self, session_id: str) -> list[dict[str, Any]]:
        with self._session_factory() as db:
            if db.get(V3SandboxSessionRecord, session_id) is None:
                raise V3SandboxSessionNotFound(session_id)
            records = (
                db.scalars(
                    select(V3SandboxMemoryTransitionEventRecord)
                    .where(V3SandboxMemoryTransitionEventRecord.session_id == session_id)
                    .order_by(
                        V3SandboxMemoryTransitionEventRecord.created_at,
                        V3SandboxMemoryTransitionEventRecord.transition_event_id,
                    )
                )
                .all()
            )
            return [
                {
                    "id": item.transition_event_id,
                    "transition_type": item.transition_type,
                    "memory_id": item.memory_id,
                    "before_status": item.before_status,
                    "after_status": item.after_status,
                    "superseded_by": item.superseded_by,
                    "trace_event_id": item.trace_event_id,
                    "turn_id": item.turn_id,
                    "action_index": item.action_index,
                    "payload": item.payload_json,
                    "created_at": item.created_at,
                }
                for item in records
            ]

    def inspection_counts(self, session_id: str) -> dict[str, int]:
        with self._session_factory() as db:
            if db.get(V3SandboxSessionRecord, session_id) is None:
                raise V3SandboxSessionNotFound(session_id)
            return {
                "messages": db.query(V3SandboxMessageRecord).filter_by(session_id=session_id).count(),
                "traces": db.query(V3SandboxTraceEventRecord).filter_by(session_id=session_id).count(),
                "actions": db.query(V3SandboxActionEventRecord).filter_by(session_id=session_id).count(),
                "memory_items": db.query(V3SandboxMemoryItemRecord).filter_by(session_id=session_id).count(),
                "transitions": db.query(V3SandboxMemoryTransitionEventRecord).filter_by(session_id=session_id).count(),
            }

    def _replace_normalized_rows(self, db: Session, session: V3SandboxSession) -> None:
        for table in (
            V3SandboxMemoryTransitionEventRecord,
            V3SandboxActionEventRecord,
            V3SandboxTraceEventRecord,
            V3SandboxMessageRecord,
            V3SandboxMemoryItemRecord,
        ):
            db.execute(delete(table).where(table.session_id == session.id))

        for message in session.messages:
            db.add(
                V3SandboxMessageRecord(
                    session_id=session.id,
                    message_id=message.id,
                    role=message.role,
                    content=message.content,
                    payload_json=message.model_dump(mode="json"),
                    created_at=message.created_at,
                )
            )

        for trace_event in session.trace:
            db.add(
                V3SandboxTraceEventRecord(
                    session_id=session.id,
                    trace_event_id=trace_event.id,
                    turn_id=trace_event.turn_id,
                    event_type=trace_event.event_type,
                    runtime_metadata_json=trace_event.runtime_metadata,
                    parsed_output_json=trace_event.parsed_output,
                    error_json=trace_event.error,
                    payload_json=trace_event.model_dump(mode="json"),
                    created_at=trace_event.created_at,
                )
            )
            for index, action in enumerate(trace_event.actions):
                db.add(
                    V3SandboxActionEventRecord(
                        session_id=session.id,
                        trace_event_id=trace_event.id,
                        action_index=index,
                        turn_id=trace_event.turn_id,
                        action_type=action.type,
                        payload_json=action.model_dump(mode="json"),
                        created_at=trace_event.created_at,
                    )
                )

        for memory in session.memory_items.values():
            db.add(
                V3SandboxMemoryItemRecord(
                    session_id=session.id,
                    memory_id=memory.id,
                    status=memory.status,
                    source=memory.source,
                    content=memory.content,
                    confidence=memory.confidence,
                    superseded_by=memory.superseded_by,
                    tags_json=memory.tags,
                    evidence_json=memory.evidence,
                    payload_json=memory.model_dump(mode="json"),
                    created_at=memory.created_at,
                    updated_at=memory.updated_at,
                )
            )

        for transition in _memory_transition_events(session):
            db.add(V3SandboxMemoryTransitionEventRecord(**transition))


def _memory_transition_events(session: V3SandboxSession) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    memory_status: dict[str, str] = {}
    for trace_event in session.trace:
        for action_index, action in enumerate(trace_event.actions):
            payload = _action_payload(action)
            if action.type == "write_memory":
                try:
                    memory = MemoryItem.model_validate(payload)
                except Exception:
                    continue
                before_status = memory_status.get(memory.id)
                events.append(
                    _transition_event(
                        session_id=session.id,
                        trace_event_id=trace_event.id,
                        turn_id=trace_event.turn_id,
                        action_index=action_index,
                        transition_type="write_memory",
                        memory_id=memory.id,
                        before_status=before_status,
                        after_status=memory.status,
                        superseded_by=memory.superseded_by,
                        payload=payload,
                        created_at=trace_event.created_at,
                    )
                )
                memory_status[memory.id] = memory.status
                for old_id in memory.supersedes:
                    before_old_status = memory_status.get(old_id)
                    events.append(
                        _transition_event(
                            session_id=session.id,
                            trace_event_id=trace_event.id,
                            turn_id=trace_event.turn_id,
                            action_index=action_index,
                            transition_type="supersede_memory",
                            memory_id=old_id,
                            before_status=before_old_status,
                            after_status="superseded",
                            superseded_by=memory.id,
                            payload={"superseded_by": memory.id, "source_memory_id": memory.id},
                            created_at=trace_event.created_at,
                        )
                    )
                    memory_status[old_id] = "superseded"
            elif action.type == "update_memory_status":
                memory_id = payload.get("memory_id")
                status = payload.get("status")
                if not isinstance(memory_id, str) or not isinstance(status, str):
                    continue
                events.append(
                    _transition_event(
                        session_id=session.id,
                        trace_event_id=trace_event.id,
                        turn_id=trace_event.turn_id,
                        action_index=action_index,
                        transition_type="update_memory_status",
                        memory_id=memory_id,
                        before_status=memory_status.get(memory_id),
                        after_status=status,
                        superseded_by=payload.get("superseded_by") if isinstance(payload.get("superseded_by"), str) else None,
                        payload=payload,
                        created_at=trace_event.created_at,
                    )
                )
                memory_status[memory_id] = status
    return events


def _transition_event(
    *,
    session_id: str,
    trace_event_id: str,
    turn_id: str,
    action_index: int,
    transition_type: str,
    memory_id: str,
    before_status: str | None,
    after_status: str | None,
    superseded_by: str | None,
    payload: dict[str, Any],
    created_at,
) -> dict[str, Any]:
    transition_event_id = f"{trace_event_id}:{action_index}:{transition_type}:{memory_id}"
    return {
        "session_id": session_id,
        "transition_event_id": transition_event_id,
        "trace_event_id": trace_event_id,
        "turn_id": turn_id,
        "action_index": action_index,
        "transition_type": transition_type,
        "memory_id": memory_id,
        "before_status": before_status,
        "after_status": after_status,
        "superseded_by": superseded_by,
        "payload_json": payload,
        "created_at": created_at or utc_now(),
    }


def _action_payload(action: AgentAction) -> dict[str, Any]:
    nested = action.payload.get(action.type)
    if isinstance(nested, dict):
        return nested
    return action.payload
