import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  AlertTriangle,
  Bot,
  Brain,
  Database,
  ListRestart,
  MessageSquareText,
  Play,
  RefreshCw,
  Send,
  Server,
  Sparkles,
} from "lucide-react";
import {
  ApiError,
  createSession,
  createTurn,
  getHealth,
  getSession,
  getTrace,
  MemoryItem,
  MemoryStatus,
  V3SandboxSession,
  V3SandboxTraceEvent,
} from "./api";

type BackendState = "checking" | "online" | "offline";

const statusOrder: MemoryStatus[] = ["observed", "confirmed", "hypothesis", "inferred", "superseded", "rejected"];

export function App() {
  const [backendState, setBackendState] = useState<BackendState>("checking");
  const [session, setSession] = useState<V3SandboxSession | null>(null);
  const [trace, setTrace] = useState<V3SandboxTraceEvent[]>([]);
  const [input, setInput] = useState("我们做面向苏州小企业老板的销售管理培训，主要是线下课。");
  const [error, setError] = useState<ApiError | Error | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    void checkBackend();
  }, []);

  const memoryItems = useMemo(() => {
    const items = Object.values(session?.memory_items ?? {});
    return items.sort((left, right) => {
      const byStatus = statusOrder.indexOf(left.status) - statusOrder.indexOf(right.status);
      if (byStatus !== 0) {
        return byStatus;
      }
      return right.updated_at.localeCompare(left.updated_at);
    });
  }, [session]);

  async function checkBackend() {
    setBackendState("checking");
    try {
      await getHealth();
      setBackendState("online");
    } catch (caught) {
      setBackendState("offline");
      setError(caught instanceof Error ? caught : new Error("backend offline"));
    }
  }

  async function handleCreateSession() {
    setIsBusy(true);
    setError(null);
    try {
      const created = await createSession();
      setSession(created);
      setTrace(created.trace);
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("create session failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleRefresh() {
    if (!session) {
      await checkBackend();
      return;
    }
    setIsBusy(true);
    setError(null);
    try {
      const [nextSession, nextTrace] = await Promise.all([getSession(session.id), getTrace(session.id)]);
      setSession(nextSession);
      setTrace(nextTrace);
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("refresh failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !input.trim()) {
      return;
    }
    setIsBusy(true);
    setError(null);
    try {
      const updated = await createTurn(session.id, input.trim());
      setSession(updated);
      setTrace(updated.trace);
      setInput("");
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("turn failed"));
      try {
        const [nextSession, nextTrace] = await Promise.all([getSession(session.id), getTrace(session.id)]);
        setSession(nextSession);
        setTrace(nextTrace);
      } catch {
        // Keep the original backend error visible.
      }
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">OpenClaw V3</div>
          <h1>Sales Agent Lab</h1>
        </div>
        <div className="topbar-actions">
          <StatusPill state={backendState} />
          <button type="button" className="icon-button" onClick={checkBackend} aria-label="Check backend">
            <RefreshCw size={16} />
          </button>
          <button type="button" className="primary-button" onClick={handleCreateSession} disabled={isBusy}>
            <Play size={16} />
            New session
          </button>
        </div>
      </header>

      <section className="session-strip" aria-label="Current session">
        <div>
          <span className="muted-label">Session</span>
          <strong data-testid="session-id">{session?.id ?? "None"}</strong>
        </div>
        <div>
          <span className="muted-label">Messages</span>
          <strong>{session?.messages.length ?? 0}</strong>
        </div>
        <div>
          <span className="muted-label">Memory</span>
          <strong>{memoryItems.length}</strong>
        </div>
        <div>
          <span className="muted-label">Trace</span>
          <strong>{trace.length}</strong>
        </div>
        <button type="button" className="secondary-button" onClick={handleRefresh} disabled={isBusy}>
          <ListRestart size={16} />
          Refresh
        </button>
      </section>

      {error ? <ErrorBanner error={error} /> : null}

      <section className="lab-grid">
        <Panel title="Conversation" icon={<MessageSquareText size={18} />}>
          <MessageTimeline session={session} />
          <form className="turn-form" onSubmit={handleSubmit}>
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Enter a sales-agent turn..."
              disabled={!session || isBusy}
            />
            <button type="submit" className="primary-button" disabled={!session || isBusy || !input.trim()}>
              <Send size={16} />
              Send turn
            </button>
          </form>
        </Panel>

        <Panel title="Memory" icon={<Brain size={18} />}>
          <MemoryList items={memoryItems} />
        </Panel>

        <div className="stacked-panels">
          <Panel title="Working State" icon={<Sparkles size={18} />}>
            <WorkingState session={session} />
          </Panel>
          <Panel title="Customer Intelligence" icon={<Database size={18} />}>
            <CustomerIntelligence session={session} />
          </Panel>
          <Panel title="Trace / Actions" icon={<Bot size={18} />}>
            <TraceList trace={trace} />
          </Panel>
        </div>
      </section>
    </main>
  );
}

function StatusPill({ state }: { state: BackendState }) {
  return (
    <span className={`status-pill status-${state}`}>
      <Server size={14} />
      {state === "checking" ? "Checking" : state === "online" ? "Backend online" : "Backend offline"}
    </span>
  );
}

function ErrorBanner({ error }: { error: ApiError | Error }) {
  const code = error instanceof ApiError ? error.code : "client_error";
  return (
    <section className="error-banner" role="alert">
      <AlertTriangle size={18} />
      <div>
        <strong>{code}</strong>
        <p>{error.message}</p>
      </div>
    </section>
  );
}

function Panel({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <section className="panel">
      <div className="panel-title">
        {icon}
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function MessageTimeline({ session }: { session: V3SandboxSession | null }) {
  if (!session?.messages.length) {
    return <EmptyState text="Create a session, then send a turn." />;
  }
  return (
    <div className="message-list">
      {session.messages.map((message) => (
        <article className={`message message-${message.role}`} key={message.id}>
          <div className="row-between">
            <strong>{message.role}</strong>
            <span>{formatTime(message.created_at)}</span>
          </div>
          <p>{message.content}</p>
        </article>
      ))}
    </div>
  );
}

function MemoryList({ items }: { items: MemoryItem[] }) {
  if (!items.length) {
    return <EmptyState text="No memory items yet." />;
  }
  return (
    <div className="memory-list">
      {items.map((item) => (
        <article className="memory-item" key={item.id}>
          <div className="row-between">
            <span className={`memory-status memory-${item.status}`}>{item.status}</span>
            <span>{Math.round(item.confidence * 100)}%</span>
          </div>
          <h3>{item.content}</h3>
          <p>{item.id}</p>
          <div className="tag-row">
            {item.tags.map((tag) => (
              <span className="tag" key={tag}>
                {tag}
              </span>
            ))}
          </div>
          {item.superseded_by ? <small>superseded by {item.superseded_by}</small> : null}
        </article>
      ))}
    </div>
  );
}

function WorkingState({ session }: { session: V3SandboxSession | null }) {
  const state = session?.working_state;
  if (!state) {
    return <EmptyState text="No working state loaded." />;
  }
  return (
    <div className="state-grid">
      <FieldList title="Product" values={state.product_understanding} />
      <FieldList title="Strategy" values={state.sales_strategy} />
      <FieldList title="Hypotheses" values={state.current_hypotheses} />
      <FieldList title="Corrections" values={state.correction_summary} />
      <FieldList title="Open questions" values={state.open_questions} />
    </div>
  );
}

function CustomerIntelligence({ session }: { session: V3SandboxSession | null }) {
  const draft = session?.customer_intelligence;
  if (!draft) {
    return <EmptyState text="No customer intelligence loaded." />;
  }
  return (
    <div className="customer-block">
      <FieldList title="Industries" values={draft.target_industries} />
      <FieldList title="Roles" values={draft.target_roles} />
      <FieldList title="Ranking reasons" values={draft.ranking_reasons} />
      <FieldList title="Validation signals" values={draft.validation_signals} />
      <div className="candidate-list">
        {draft.candidates.map((candidate) => (
          <article className="candidate" key={candidate.id}>
            <div className="row-between">
              <strong>{candidate.name}</strong>
              <span>{candidate.score}</span>
            </div>
            <p>{candidate.ranking_reason || candidate.segment}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function TraceList({ trace }: { trace: V3SandboxTraceEvent[] }) {
  if (!trace.length) {
    return <EmptyState text="No trace events yet." />;
  }
  return (
    <div className="trace-list">
      {trace
        .slice()
        .reverse()
        .map((event) => (
          <article className="trace-event" key={event.id}>
            <div className="row-between">
              <strong>{event.event_type}</strong>
              <span>{formatTime(event.created_at)}</span>
            </div>
            {event.error ? <p className="trace-error">{event.error.code}</p> : null}
            <p>{event.actions.map((action) => action.type).join(", ") || "no actions"}</p>
            <pre>{JSON.stringify(event.runtime_metadata, null, 2)}</pre>
          </article>
        ))}
    </div>
  );
}

function FieldList({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="field-list">
      <strong>{title}</strong>
      {values.length ? (
        <ul>
          {values.map((value) => (
            <li key={value}>{value}</li>
          ))}
        </ul>
      ) : (
        <span>Empty</span>
      )}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <p className="empty-state">{text}</p>;
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}
