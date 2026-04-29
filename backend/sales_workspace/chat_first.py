from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session, sessionmaker

from backend.api.database import get_session_factory
from backend.sales_workspace.schemas import SalesWorkspace, utc_now
from backend.sales_workspace.store import WorkspaceNotFound


class ChatFirstModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


MessageRole = Literal["user", "assistant", "system"]
MessageType = Literal[
    "product_profile_update",
    "lead_direction_update",
    "mixed_product_and_direction_update",
    "clarifying_question",
    "workspace_question",
    "draft_summary",
    "out_of_scope_v2_2",
    "system_note",
]
AgentRunStatus = Literal["queued", "running", "succeeded", "failed"]
DefaultConversationThreadId = "main"


class ConversationThread(ChatFirstModel):
    id: str
    workspace_id: str
    title: str
    status: Literal["active", "archived"] = "active"
    created_at: Any = Field(default_factory=utc_now)
    updated_at: Any = Field(default_factory=utc_now)


class ConversationMessage(ChatFirstModel):
    id: str
    workspace_id: str
    thread_id: str = DefaultConversationThreadId
    role: MessageRole
    message_type: MessageType
    content: str
    linked_object_refs: list[str] = Field(default_factory=list)
    created_by_agent_run_id: str | None = None
    created_at: Any = Field(default_factory=utc_now)


class SalesAgentTurnRun(ChatFirstModel):
    id: str
    workspace_id: str
    thread_id: str = DefaultConversationThreadId
    run_type: Literal["sales_agent_turn"] = "sales_agent_turn"
    status: AgentRunStatus = "queued"
    input_refs: list[str] = Field(default_factory=list)
    output_refs: list[str] = Field(default_factory=list)
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)
    error: dict[str, Any] | None = None
    created_at: Any = Field(default_factory=utc_now)
    started_at: Any | None = None
    finished_at: Any | None = None


class SalesAgentTurnContextPack(ChatFirstModel):
    id: str
    workspace_id: str
    thread_id: str = DefaultConversationThreadId
    agent_run_id: str
    task_type: Literal["sales_agent_turn"] = "sales_agent_turn"
    token_budget_chars: int = 6000
    workspace_summary: str
    current_product_profile_revision: dict[str, Any] | None = None
    current_lead_direction_version: dict[str, Any] | None = None
    recent_messages: list[dict[str, Any]] = Field(default_factory=list)
    active_draft_review_summary: dict[str, Any] | None = None
    open_questions: list[str] = Field(default_factory=list)
    blocked_capabilities: list[str] = Field(default_factory=lambda: ["V2.2 evidence/search/contact"])
    kernel_boundary: str = (
        "Runtime returns WorkspacePatchDraft; Sales Workspace Kernel validates and writes formal objects."
    )
    input_refs: list[str] = Field(default_factory=list)
    source_versions: dict[str, Any] = Field(default_factory=dict)
    created_at: Any = Field(default_factory=utc_now)


class ChatTraceNotFound(LookupError):
    pass


sales_workspace_conversation_messages = sa.Table(
    "sales_workspace_conversation_messages",
    sa.MetaData(),
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("message_id", sa.Text(), primary_key=True),
    sa.Column("thread_id", sa.Text(), nullable=False, server_default=DefaultConversationThreadId),
    sa.Column("role", sa.Text(), nullable=False),
    sa.Column("message_type", sa.Text(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("linked_object_refs_json", sa.JSON(), nullable=False),
    sa.Column("created_by_agent_run_id", sa.Text(), nullable=True),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_agent_runs = sa.Table(
    "sales_workspace_agent_runs",
    sa.MetaData(),
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("agent_run_id", sa.Text(), primary_key=True),
    sa.Column("thread_id", sa.Text(), nullable=False, server_default=DefaultConversationThreadId),
    sa.Column("run_type", sa.Text(), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("input_refs_json", sa.JSON(), nullable=False),
    sa.Column("output_refs_json", sa.JSON(), nullable=False),
    sa.Column("runtime_metadata_json", sa.JSON(), nullable=False),
    sa.Column("error_json", sa.JSON(), nullable=True),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
)

sales_workspace_context_packs = sa.Table(
    "sales_workspace_context_packs",
    sa.MetaData(),
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("context_pack_id", sa.Text(), primary_key=True),
    sa.Column("thread_id", sa.Text(), nullable=False, server_default=DefaultConversationThreadId),
    sa.Column("agent_run_id", sa.Text(), nullable=False),
    sa.Column("task_type", sa.Text(), nullable=False),
    sa.Column("token_budget_chars", sa.Integer(), nullable=False),
    sa.Column("input_refs_json", sa.JSON(), nullable=False),
    sa.Column("source_versions_json", sa.JSON(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

sales_workspace_conversation_threads = sa.Table(
    "sales_workspace_conversation_threads",
    sa.MetaData(),
    sa.Column("workspace_id", sa.Text(), primary_key=True),
    sa.Column("thread_id", sa.Text(), primary_key=True),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("payload_json", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)


class InMemoryChatTraceStore:
    def __init__(self) -> None:
        self._threads: dict[tuple[str, str], ConversationThread] = {}
        self._messages: dict[tuple[str, str], ConversationMessage] = {}
        self._agent_runs: dict[tuple[str, str], SalesAgentTurnRun] = {}
        self._context_packs: dict[tuple[str, str], SalesAgentTurnContextPack] = {}

    def save_thread(self, thread: ConversationThread) -> None:
        self._threads[(thread.workspace_id, thread.id)] = thread

    def get_thread(self, workspace_id: str, thread_id: str) -> ConversationThread:
        self.ensure_thread(workspace_id, thread_id)
        try:
            return self._threads[(workspace_id, thread_id)]
        except KeyError as exc:
            raise ChatTraceNotFound(thread_id) from exc

    def list_threads(self, workspace_id: str, *, ensure_default: bool = True) -> list[ConversationThread]:
        if ensure_default:
            self.ensure_thread(workspace_id, DefaultConversationThreadId)
        return sorted(
            [thread for (stored_workspace_id, _), thread in self._threads.items() if stored_workspace_id == workspace_id],
            key=lambda thread: thread.updated_at,
            reverse=True,
        )

    def ensure_thread(self, workspace_id: str, thread_id: str = DefaultConversationThreadId) -> None:
        key = (workspace_id, thread_id)
        if key not in self._threads and thread_id == DefaultConversationThreadId:
            self._threads[key] = ConversationThread(
                id=DefaultConversationThreadId,
                workspace_id=workspace_id,
                title="主对话",
            )

    def save_message(self, message: ConversationMessage) -> None:
        self._messages[(message.workspace_id, message.id)] = message
        self.ensure_thread(message.workspace_id, message.thread_id)

    def get_message(self, workspace_id: str, message_id: str) -> ConversationMessage:
        try:
            return self._messages[(workspace_id, message_id)]
        except KeyError as exc:
            raise ChatTraceNotFound(message_id) from exc

    def list_messages(
        self,
        workspace_id: str,
        thread_id: str = DefaultConversationThreadId,
    ) -> list[ConversationMessage]:
        self.ensure_thread(workspace_id, thread_id)
        return sorted(
            [
                message
                for (stored_workspace_id, _), message in self._messages.items()
                if stored_workspace_id == workspace_id and message.thread_id == thread_id
            ],
            key=lambda message: message.created_at,
        )

    def save_agent_run(self, agent_run: SalesAgentTurnRun) -> None:
        self._agent_runs[(agent_run.workspace_id, agent_run.id)] = agent_run

    def get_agent_run(self, workspace_id: str, agent_run_id: str) -> SalesAgentTurnRun:
        try:
            return self._agent_runs[(workspace_id, agent_run_id)]
        except KeyError as exc:
            raise ChatTraceNotFound(agent_run_id) from exc

    def list_agent_runs(
        self,
        workspace_id: str,
        thread_id: str | None = None,
    ) -> list[SalesAgentTurnRun]:
        return sorted(
            [
                agent_run
                for (stored_workspace_id, _), agent_run in self._agent_runs.items()
                if stored_workspace_id == workspace_id and (thread_id is None or agent_run.thread_id == thread_id)
            ],
            key=lambda agent_run: agent_run.created_at,
            reverse=True,
        )

    def save_context_pack(self, context_pack: SalesAgentTurnContextPack) -> None:
        self._context_packs[(context_pack.workspace_id, context_pack.id)] = context_pack

    def get_context_pack(self, workspace_id: str, context_pack_id: str) -> SalesAgentTurnContextPack:
        try:
            return self._context_packs[(workspace_id, context_pack_id)]
        except KeyError as exc:
            raise ChatTraceNotFound(context_pack_id) from exc

    def list_context_packs(
        self,
        workspace_id: str,
        thread_id: str | None = None,
        agent_run_id: str | None = None,
    ) -> list[SalesAgentTurnContextPack]:
        return sorted(
            [
                context_pack
                for (stored_workspace_id, _), context_pack in self._context_packs.items()
                if (
                    stored_workspace_id == workspace_id
                    and (thread_id is None or context_pack.thread_id == thread_id)
                    and (agent_run_id is None or context_pack.agent_run_id == agent_run_id)
                )
            ],
            key=lambda context_pack: context_pack.created_at,
            reverse=True,
        )


class PostgresChatTraceStore:
    def __init__(self, session_factory: sessionmaker[Session] | Callable[[], Session] | None = None) -> None:
        self._session_factory = session_factory or get_session_factory()

    def save_thread(self, thread: ConversationThread) -> None:
        values = {
            "workspace_id": thread.workspace_id,
            "thread_id": thread.id,
            "title": thread.title,
            "status": thread.status,
            "payload_json": _json(thread),
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
        }
        with self._session_factory() as session:
            with session.begin():
                updated = session.execute(
                    sales_workspace_conversation_threads.update()
                    .where(
                        sales_workspace_conversation_threads.c.workspace_id == thread.workspace_id,
                        sales_workspace_conversation_threads.c.thread_id == thread.id,
                    )
                    .values(**values)
                ).rowcount
                if not updated:
                    session.execute(sales_workspace_conversation_threads.insert().values(**values))

    def get_thread(self, workspace_id: str, thread_id: str) -> ConversationThread:
        self.ensure_thread(workspace_id, thread_id)
        with self._session_factory() as session:
            row = session.execute(
                sa.select(sales_workspace_conversation_threads.c.payload_json).where(
                    sales_workspace_conversation_threads.c.workspace_id == workspace_id,
                    sales_workspace_conversation_threads.c.thread_id == thread_id,
                )
            ).first()
            if row is None:
                raise ChatTraceNotFound(thread_id)
            return ConversationThread.model_validate(row.payload_json)

    def list_threads(self, workspace_id: str, *, ensure_default: bool = True) -> list[ConversationThread]:
        if ensure_default:
            self.ensure_thread(workspace_id, DefaultConversationThreadId)
        with self._session_factory() as session:
            rows = session.execute(
                sa.select(sales_workspace_conversation_threads.c.payload_json)
                .where(sales_workspace_conversation_threads.c.workspace_id == workspace_id)
                .order_by(sales_workspace_conversation_threads.c.updated_at.desc())
            )
            return [ConversationThread.model_validate(row.payload_json) for row in rows]

    def ensure_thread(self, workspace_id: str, thread_id: str = DefaultConversationThreadId) -> None:
        if thread_id != DefaultConversationThreadId:
            return
        with self._session_factory() as session:
            row = session.execute(
                sa.select(sales_workspace_conversation_threads.c.thread_id).where(
                    sales_workspace_conversation_threads.c.workspace_id == workspace_id,
                    sales_workspace_conversation_threads.c.thread_id == DefaultConversationThreadId,
                )
            ).first()
        if row is None:
            self.save_thread(
                ConversationThread(
                    id=DefaultConversationThreadId,
                    workspace_id=workspace_id,
                    title="主对话",
                )
            )

    def save_message(self, message: ConversationMessage) -> None:
        self.ensure_thread(message.workspace_id, message.thread_id)
        values = {
            "workspace_id": message.workspace_id,
            "message_id": message.id,
            "thread_id": message.thread_id,
            "role": message.role,
            "message_type": message.message_type,
            "content": message.content,
            "linked_object_refs_json": message.linked_object_refs,
            "created_by_agent_run_id": message.created_by_agent_run_id,
            "payload_json": _json(message),
            "created_at": message.created_at,
        }
        with self._session_factory() as session:
            with session.begin():
                updated = session.execute(
                    sales_workspace_conversation_messages.update()
                    .where(
                        sales_workspace_conversation_messages.c.workspace_id == message.workspace_id,
                        sales_workspace_conversation_messages.c.message_id == message.id,
                    )
                    .values(**values)
                ).rowcount
                if not updated:
                    session.execute(sales_workspace_conversation_messages.insert().values(**values))

    def get_message(self, workspace_id: str, message_id: str) -> ConversationMessage:
        with self._session_factory() as session:
            row = session.execute(
                sa.select(sales_workspace_conversation_messages.c.payload_json).where(
                    sales_workspace_conversation_messages.c.workspace_id == workspace_id,
                    sales_workspace_conversation_messages.c.message_id == message_id,
                )
            ).first()
            if row is None:
                raise ChatTraceNotFound(message_id)
            return ConversationMessage.model_validate(row.payload_json)

    def list_messages(
        self,
        workspace_id: str,
        thread_id: str = DefaultConversationThreadId,
    ) -> list[ConversationMessage]:
        self.ensure_thread(workspace_id, thread_id)
        with self._session_factory() as session:
            rows = session.execute(
                sa.select(sales_workspace_conversation_messages.c.payload_json)
                .where(
                    sales_workspace_conversation_messages.c.workspace_id == workspace_id,
                    sales_workspace_conversation_messages.c.thread_id == thread_id,
                )
                .order_by(sales_workspace_conversation_messages.c.created_at)
            )
            return [ConversationMessage.model_validate(row.payload_json) for row in rows]

    def save_agent_run(self, agent_run: SalesAgentTurnRun) -> None:
        values = {
            "workspace_id": agent_run.workspace_id,
            "agent_run_id": agent_run.id,
            "thread_id": agent_run.thread_id,
            "run_type": agent_run.run_type,
            "status": agent_run.status,
            "input_refs_json": agent_run.input_refs,
            "output_refs_json": agent_run.output_refs,
            "runtime_metadata_json": agent_run.runtime_metadata,
            "error_json": agent_run.error,
            "payload_json": _json(agent_run),
            "created_at": agent_run.created_at,
            "started_at": agent_run.started_at,
            "finished_at": agent_run.finished_at,
        }
        with self._session_factory() as session:
            with session.begin():
                updated = session.execute(
                    sales_workspace_agent_runs.update()
                    .where(
                        sales_workspace_agent_runs.c.workspace_id == agent_run.workspace_id,
                        sales_workspace_agent_runs.c.agent_run_id == agent_run.id,
                    )
                    .values(**values)
                ).rowcount
                if not updated:
                    session.execute(sales_workspace_agent_runs.insert().values(**values))

    def get_agent_run(self, workspace_id: str, agent_run_id: str) -> SalesAgentTurnRun:
        with self._session_factory() as session:
            row = session.execute(
                sa.select(sales_workspace_agent_runs.c.payload_json).where(
                    sales_workspace_agent_runs.c.workspace_id == workspace_id,
                    sales_workspace_agent_runs.c.agent_run_id == agent_run_id,
                )
            ).first()
            if row is None:
                raise ChatTraceNotFound(agent_run_id)
            return SalesAgentTurnRun.model_validate(row.payload_json)

    def list_agent_runs(
        self,
        workspace_id: str,
        thread_id: str | None = None,
    ) -> list[SalesAgentTurnRun]:
        statement = sa.select(sales_workspace_agent_runs.c.payload_json).where(
            sales_workspace_agent_runs.c.workspace_id == workspace_id
        )
        if thread_id is not None:
            statement = statement.where(sales_workspace_agent_runs.c.thread_id == thread_id)
        statement = statement.order_by(sales_workspace_agent_runs.c.created_at.desc())
        with self._session_factory() as session:
            rows = session.execute(statement)
            return [SalesAgentTurnRun.model_validate(row.payload_json) for row in rows]

    def save_context_pack(self, context_pack: SalesAgentTurnContextPack) -> None:
        values = {
            "workspace_id": context_pack.workspace_id,
            "context_pack_id": context_pack.id,
            "thread_id": context_pack.thread_id,
            "agent_run_id": context_pack.agent_run_id,
            "task_type": context_pack.task_type,
            "token_budget_chars": context_pack.token_budget_chars,
            "input_refs_json": context_pack.input_refs,
            "source_versions_json": context_pack.source_versions,
            "payload_json": _json(context_pack),
            "created_at": context_pack.created_at,
        }
        with self._session_factory() as session:
            with session.begin():
                updated = session.execute(
                    sales_workspace_context_packs.update()
                    .where(
                        sales_workspace_context_packs.c.workspace_id == context_pack.workspace_id,
                        sales_workspace_context_packs.c.context_pack_id == context_pack.id,
                    )
                    .values(**values)
                ).rowcount
                if not updated:
                    session.execute(sales_workspace_context_packs.insert().values(**values))

    def get_context_pack(self, workspace_id: str, context_pack_id: str) -> SalesAgentTurnContextPack:
        with self._session_factory() as session:
            row = session.execute(
                sa.select(sales_workspace_context_packs.c.payload_json).where(
                    sales_workspace_context_packs.c.workspace_id == workspace_id,
                    sales_workspace_context_packs.c.context_pack_id == context_pack_id,
                )
            ).first()
            if row is None:
                raise ChatTraceNotFound(context_pack_id)
            return SalesAgentTurnContextPack.model_validate(row.payload_json)

    def list_context_packs(
        self,
        workspace_id: str,
        thread_id: str | None = None,
        agent_run_id: str | None = None,
    ) -> list[SalesAgentTurnContextPack]:
        statement = sa.select(sales_workspace_context_packs.c.payload_json).where(
            sales_workspace_context_packs.c.workspace_id == workspace_id
        )
        if thread_id is not None:
            statement = statement.where(sales_workspace_context_packs.c.thread_id == thread_id)
        if agent_run_id is not None:
            statement = statement.where(sales_workspace_context_packs.c.agent_run_id == agent_run_id)
        statement = statement.order_by(sales_workspace_context_packs.c.created_at.desc())
        with self._session_factory() as session:
            rows = session.execute(statement)
            return [SalesAgentTurnContextPack.model_validate(row.payload_json) for row in rows]


def compile_sales_agent_turn_context_pack(
    workspace: SalesWorkspace,
    *,
    thread_id: str = DefaultConversationThreadId,
    agent_run_id: str,
    context_pack_id: str,
    recent_messages: list[ConversationMessage],
    token_budget_chars: int = 6000,
) -> SalesAgentTurnContextPack:
    product = (
        workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id)
        if workspace.current_product_profile_revision_id
        else None
    )
    direction = (
        workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id)
        if workspace.current_lead_direction_version_id
        else None
    )
    return SalesAgentTurnContextPack(
        id=context_pack_id,
        workspace_id=workspace.id,
        thread_id=thread_id,
        agent_run_id=agent_run_id,
        token_budget_chars=token_budget_chars,
        workspace_summary=f"{workspace.name} workspace",
        current_product_profile_revision=product.model_dump(mode="json") if product else None,
        current_lead_direction_version=direction.model_dump(mode="json") if direction else None,
        recent_messages=[
            {
                "id": message.id,
                "role": message.role,
                "message_type": message.message_type,
                "content_excerpt": message.content[:500],
            }
            for message in recent_messages[-12:]
        ],
        input_refs=[
            f"SalesWorkspace:{workspace.id}",
            f"ConversationThread:{thread_id}",
            *[f"ConversationMessage:{message.id}" for message in recent_messages[-12:]],
        ],
        source_versions={
            "workspace_version": workspace.workspace_version,
            "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
            "current_lead_direction_version_id": workspace.current_lead_direction_version_id,
        },
    )


def next_trace_id(prefix: str, existing_count: int) -> str:
    return f"{prefix}_{existing_count + 1:03d}"


def _json(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")
