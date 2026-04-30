import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  AlertTriangle,
  Bot,
  Brain,
  Database,
  FlaskConical,
  ListRestart,
  MessageSquareText,
  PanelTopOpen,
  Play,
  RefreshCw,
  RotateCcw,
  Send,
  Server,
  Settings,
  Sparkles,
  X,
} from "lucide-react";
import {
  ApiError,
  createDemoSeed,
  createSession,
  createTurn,
  CoreMemoryBlock,
  getHealth,
  getCoreMemoryTransitions,
  getMemoryTransitions,
  getRuntimeConfig,
  getSession,
  getStoreStatus,
  getTrace,
  MemoryItem,
  MemoryStatus,
  resetRuntimeConfig,
  updateRuntimeConfig,
  V3SandboxDebugTraceEvent,
  V3SandboxDebugTraceOptions,
  V3SandboxCoreMemoryTransitionsResponse,
  V3SandboxRuntimeConfig,
  replaySession,
  V3SandboxMemoryTransitionsResponse,
  V3SandboxReplayReport,
  V3SandboxSession,
  V3SandboxStoreStatus,
  V3SandboxTraceEvent,
} from "./api";

type BackendState = "checking" | "online" | "offline";

const statusOrder: MemoryStatus[] = ["observed", "confirmed", "hypothesis", "inferred", "superseded", "rejected"];

const defaultTraceOptions: V3SandboxDebugTraceOptions = {
  verbose: false,
  include_prompt: false,
  include_raw_llm_output: false,
  include_repair_attempts: false,
  include_node_io: false,
  include_state_diff: false,
  max_bytes: 80_000,
};

function traceOptionsFromRuntimeConfig(config: V3SandboxRuntimeConfig["runtime_config"]): V3SandboxDebugTraceOptions {
  return {
    verbose: config.default_debug_trace,
    include_prompt: config.default_include_prompt,
    include_raw_llm_output: config.default_include_raw_llm_output,
    include_repair_attempts: config.default_debug_trace,
    include_node_io: config.default_debug_trace,
    include_state_diff: config.default_include_state_diff,
    max_bytes: config.trace_max_bytes,
  };
}

export function App() {
  const [backendState, setBackendState] = useState<BackendState>("checking");
  const [session, setSession] = useState<V3SandboxSession | null>(null);
  const [trace, setTrace] = useState<V3SandboxTraceEvent[]>([]);
  const [storeStatus, setStoreStatus] = useState<V3SandboxStoreStatus | null>(null);
  const [runtimeConfig, setRuntimeConfig] = useState<V3SandboxRuntimeConfig | null>(null);
  const [runtimeDraft, setRuntimeDraft] = useState<V3SandboxRuntimeConfig["runtime_config"] | null>(null);
  const [transitionInspection, setTransitionInspection] = useState<V3SandboxMemoryTransitionsResponse | null>(null);
  const [coreTransitionInspection, setCoreTransitionInspection] = useState<V3SandboxCoreMemoryTransitionsResponse | null>(null);
  const [input, setInput] = useState("我们做面向苏州小企业老板的销售管理培训，主要是线下课。");
  const [error, setError] = useState<ApiError | Error | null>(null);
  const [replayReport, setReplayReport] = useState<V3SandboxReplayReport | null>(null);
  const [traceOptions, setTraceOptions] = useState<V3SandboxDebugTraceOptions>(defaultTraceOptions);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isTraceInspectorOpen, setIsTraceInspectorOpen] = useState(false);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
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
      setStoreStatus(await getStoreStatus());
      const config = await getRuntimeConfig();
      setRuntimeConfig(config);
      setRuntimeDraft(config.runtime_config);
      setTraceOptions(traceOptionsFromRuntimeConfig(config.runtime_config));
      setBackendState("online");
    } catch (caught) {
      setBackendState("offline");
      setError(caught instanceof Error ? caught : new Error("backend offline"));
    }
  }

  async function refreshInspection(sessionId: string | null) {
    const nextStore = await getStoreStatus();
    const config = await getRuntimeConfig();
    setStoreStatus(nextStore);
    setRuntimeConfig(config);
    setRuntimeDraft(config.runtime_config);
    setTraceOptions(traceOptionsFromRuntimeConfig(config.runtime_config));
    if (!sessionId) {
      setTransitionInspection(null);
      setCoreTransitionInspection(null);
      return;
    }
    const [memoryTransitions, coreMemoryTransitions] = await Promise.all([
      getMemoryTransitions(sessionId),
      getCoreMemoryTransitions(sessionId),
    ]);
    setTransitionInspection(memoryTransitions);
    setCoreTransitionInspection(coreMemoryTransitions);
  }

  async function handleCreateSession() {
    setIsBusy(true);
    setError(null);
    try {
      const created = await createSession();
      setSession(created);
      setTrace(created.trace);
      setReplayReport(null);
      await refreshInspection(created.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("create session failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleSeedDemo() {
    setIsBusy(true);
    setError(null);
    setReplayReport(null);
    try {
      const seeded = await createDemoSeed();
      setSession(seeded);
      setTrace(seeded.trace);
      await refreshInspection(seeded.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("seed demo failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleResetSession() {
    setIsBusy(true);
    setError(null);
    setReplayReport(null);
    try {
      const created = await createSession("V3 Sales Agent Lab Reset");
      setSession(created);
      setTrace(created.trace);
      await refreshInspection(created.id);
      setInput("我们做面向苏州小企业老板的销售管理培训，主要是线下课。");
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("reset session failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleReplaySession() {
    if (!session) {
      return;
    }
    setIsBusy(true);
    setError(null);
    setReplayReport(null);
    try {
      const result = await replaySession(session.id);
      setSession(result.session);
      setTrace(result.session.trace);
      setReplayReport(result.replay);
      await refreshInspection(result.session.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("replay failed"));
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
      const [nextSession, nextTrace, nextTransitions, nextCoreTransitions, nextStore, nextConfig] = await Promise.all([
        getSession(session.id),
        getTrace(session.id),
        getMemoryTransitions(session.id),
        getCoreMemoryTransitions(session.id),
        getStoreStatus(),
        getRuntimeConfig(),
      ]);
      setSession(nextSession);
      setTrace(nextTrace);
      setTransitionInspection(nextTransitions);
      setCoreTransitionInspection(nextCoreTransitions);
      setStoreStatus(nextStore);
      setRuntimeConfig(nextConfig);
      setRuntimeDraft(nextConfig.runtime_config);
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("refresh failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function refreshRuntimeConfig() {
    const config = await getRuntimeConfig();
    setRuntimeConfig(config);
    setRuntimeDraft(config.runtime_config);
    setStoreStatus(config.backend_status.store);
    setTraceOptions(traceOptionsFromRuntimeConfig(config.runtime_config));
  }

  async function handleApplyRuntimeConfig() {
    if (!runtimeDraft) {
      return;
    }
    setIsBusy(true);
    setError(null);
    try {
      const updated = await updateRuntimeConfig(runtimeDraft);
      setRuntimeConfig(updated);
      setRuntimeDraft(updated.runtime_config);
      setStoreStatus(updated.backend_status.store);
      setTraceOptions(traceOptionsFromRuntimeConfig(updated.runtime_config));
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("runtime config update failed"));
    } finally {
      setIsBusy(false);
    }
  }

  async function handleResetRuntimeConfig() {
    setIsBusy(true);
    setError(null);
    try {
      const reset = await resetRuntimeConfig();
      setRuntimeConfig(reset);
      setRuntimeDraft(reset.runtime_config);
      setStoreStatus(reset.backend_status.store);
      setTraceOptions(traceOptionsFromRuntimeConfig(reset.runtime_config));
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("runtime config reset failed"));
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
      const debugTrace = traceOptions.verbose
        ? {
            ...traceOptions,
            include_repair_attempts: true,
            include_node_io: true,
            max_bytes: runtimeConfig?.runtime_config.trace_max_bytes ?? traceOptions.max_bytes,
          }
        : undefined;
      const updated = await createTurn(session.id, input.trim(), debugTrace);
      setSession(updated);
      setTrace(updated.trace);
      await refreshInspection(updated.id);
      setInput("");
    } catch (caught) {
      setError(caught instanceof Error ? caught : new Error("turn failed"));
      try {
        const [nextSession, nextTrace, nextTransitions, nextCoreTransitions, nextStore] = await Promise.all([
          getSession(session.id),
          getTrace(session.id),
          getMemoryTransitions(session.id),
          getCoreMemoryTransitions(session.id),
          getStoreStatus(),
        ]);
        setSession(nextSession);
        setTrace(nextTrace);
        setTransitionInspection(nextTransitions);
        setCoreTransitionInspection(nextCoreTransitions);
        setStoreStatus(nextStore);
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
          <button type="button" className="secondary-button" onClick={() => setIsSettingsOpen(true)}>
            <Settings size={16} />
            Settings
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
          <span className="muted-label">Store</span>
          <strong data-testid="store-backend">{storeStatus?.backend ?? "unknown"}</strong>
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

      <section className="control-strip" aria-label="Lab controls">
        <button type="button" className="secondary-button" onClick={handleSeedDemo} disabled={isBusy}>
          <FlaskConical size={16} />
          Seed demo
        </button>
        <button type="button" className="secondary-button" onClick={handleResetSession} disabled={isBusy}>
          <RotateCcw size={16} />
          Reset session
        </button>
        <button type="button" className="secondary-button" onClick={handleReplaySession} disabled={!session || isBusy}>
          <Play size={16} />
          Replay user turns
        </button>
        {replayReport ? <ReplayReport report={replayReport} /> : null}
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
            <TraceControls options={traceOptions} onChange={setTraceOptions} disabled={!session || isBusy} />
            <button type="submit" className="primary-button" disabled={!session || isBusy || !input.trim()}>
              <Send size={16} />
              Send turn
            </button>
          </form>
        </Panel>

        <div className="stacked-panels">
          <Panel title="Core Memory Blocks" icon={<Brain size={18} />}>
            <CoreMemoryBlocks blocks={session?.core_memory_blocks ?? null} />
          </Panel>
          <Panel title="Memory" icon={<Brain size={18} />}>
            <MemoryList items={memoryItems} />
          </Panel>
        </div>

        <div className="stacked-panels">
          <Panel title="Working State" icon={<Sparkles size={18} />}>
            <WorkingState session={session} />
          </Panel>
          <Panel title="Customer Intelligence" icon={<Database size={18} />}>
            <CustomerIntelligence session={session} />
          </Panel>
          <Panel title="Trace / Actions" icon={<Bot size={18} />}>
            <TraceList trace={trace} onOpenInspector={(traceId) => {
              setSelectedTraceId(traceId);
              setIsTraceInspectorOpen(true);
            }} />
          </Panel>
          <Panel title="Memory Transitions" icon={<Database size={18} />}>
            <MemoryTransitions inspection={transitionInspection} />
          </Panel>
          <Panel title="Core Memory Transitions" icon={<Database size={18} />}>
            <CoreMemoryTransitions inspection={coreTransitionInspection} />
          </Panel>
        </div>
      </section>
      {isSettingsOpen ? (
        <SettingsOverlay
          config={runtimeConfig}
          draft={runtimeDraft}
          disabled={isBusy}
          onDraftChange={setRuntimeDraft}
          onApply={handleApplyRuntimeConfig}
          onReset={handleResetRuntimeConfig}
          onRefresh={refreshRuntimeConfig}
          onClose={() => setIsSettingsOpen(false)}
        />
      ) : null}
      {isTraceInspectorOpen ? (
        <TraceInspector
          trace={trace}
          selectedTraceId={selectedTraceId}
          onSelectTrace={setSelectedTraceId}
          onClose={() => setIsTraceInspectorOpen(false)}
        />
      ) : null}
    </main>
  );
}

function ReplayReport({ report }: { report: V3SandboxReplayReport }) {
  return (
    <div className={`replay-report replay-${report.status}`} role="status">
      <strong>Replay {report.status}</strong>
      <span>{report.replayed_turns} turns</span>
      <span>{report.replay_session_id}</span>
      {report.failed_turn_index ? <span>failed at #{report.failed_turn_index}</span> : null}
      {report.error ? <span>{report.error.code}</span> : null}
    </div>
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

function SettingsOverlay({
  config,
  draft,
  disabled,
  onDraftChange,
  onApply,
  onReset,
  onRefresh,
  onClose,
}: {
  config: V3SandboxRuntimeConfig | null;
  draft: V3SandboxRuntimeConfig["runtime_config"] | null;
  disabled: boolean;
  onDraftChange: (draft: V3SandboxRuntimeConfig["runtime_config"]) => void;
  onApply: () => void;
  onReset: () => void;
  onRefresh: () => void;
  onClose: () => void;
}) {
  function update(next: Partial<V3SandboxRuntimeConfig["runtime_config"]>) {
    if (!draft) {
      return;
    }
    onDraftChange({ ...draft, ...next });
  }

  return (
    <div className="overlay-backdrop" role="dialog" aria-modal="true" aria-label="Settings">
      <section className="settings-drawer">
        <div className="overlay-header">
          <div>
            <div className="eyebrow">Lab Runtime</div>
            <h2>Settings</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close settings">
            <X size={16} />
          </button>
        </div>

        {!config || !draft ? (
          <EmptyState text="Runtime config is not loaded." />
        ) : (
          <div className="settings-content">
            <section className="settings-section">
              <h3>Backend Status</h3>
              <StatusGrid
                rows={[
                  ["Store backend", config.backend_status.store.backend],
                  ["DB enabled", yesNo(config.backend_status.store.database_enabled)],
                  ["JSON enabled", yesNo(config.backend_status.store.json_enabled)],
                  ["Memory transitions", config.backend_status.store.transition_events_supported ? "supported" : "not supported"],
                  ["LLM provider", config.backend_status.llm_provider],
                  ["LLM model", config.backend_status.llm_model],
                  ["LLM key", config.backend_status.llm_api_key_status],
                  ["LLM timeout", `${config.backend_status.llm_timeout_seconds}s`],
                  ["Native FC", config.backend_status.native_fc_supported ? "supported" : "not supported"],
                  ["Native FC role", config.backend_status.native_fc_recommended_role],
                  ["Memory runtime", config.backend_status.memory_runtime],
                  ["Native function calling", enabled(config.backend_status.native_function_calling)],
                  ["Langfuse", enabled(config.backend_status.langfuse_enabled)],
                  ["Dev LLM trace", enabled(config.backend_status.dev_llm_trace_enabled)],
                ]}
              />
            </section>

            <section className="settings-section">
              <h3>Runtime Config</h3>
              <div className="settings-form">
                <label>
                  <span>Model</span>
                  <select
                    aria-label="LLM model"
                    value={draft.llm_model}
                    onChange={(event) => update({ llm_model: event.target.value })}
                  >
                    {config.allowlists.llm_models.map((model) => (
                      <option value={model} key={model}>
                        {model} · {config.native_fc.model_policies[model]?.recommended_role ?? "candidate"}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Timeout</span>
                  <select
                    value={draft.llm_timeout_seconds}
                    onChange={(event) => update({ llm_timeout_seconds: Number(event.target.value) })}
                  >
                    {config.allowlists.llm_timeout_seconds.map((timeout) => (
                      <option value={timeout} key={timeout}>
                        {timeout}s
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Trace max bytes</span>
                  <select
                    value={draft.trace_max_bytes}
                    onChange={(event) => update({ trace_max_bytes: Number(event.target.value) })}
                  >
                    {config.allowlists.trace_max_bytes.map((bytes) => (
                      <option value={bytes} key={bytes}>
                        {Math.round(bytes / 1000)}KB
                      </option>
                    ))}
                  </select>
                </label>
                <Toggle label="Default verbose trace" checked={draft.default_debug_trace} onChange={(value) => update({ default_debug_trace: value })} />
                <Toggle label="Default include prompt" checked={draft.default_include_prompt} onChange={(value) => update({ default_include_prompt: value })} />
                <Toggle
                  label="Default include raw LLM output"
                  checked={draft.default_include_raw_llm_output}
                  onChange={(value) => update({ default_include_raw_llm_output: value })}
                />
                <Toggle
                  label="Default include state diff"
                  checked={draft.default_include_state_diff}
                  onChange={(value) => update({ default_include_state_diff: value })}
                />
                <Toggle label="Replay debug trace" checked={draft.replay_debug_trace} onChange={(value) => update({ replay_debug_trace: value })} />
              </div>
            </section>

            <section className="settings-section">
              <h3>Native FC Policy</h3>
              <StatusGrid
                rows={[
                  ["Default model", config.native_fc.default_model],
                  ["Memory runtime", config.memory_runtime.mode],
                  ["Memory tools", config.memory_runtime.tools.join(", ")],
                  ["Effective role", config.native_fc.effective_model_policy.recommended_role ?? "unknown"],
                  ["Tool choices", (config.native_fc.effective_model_policy.tool_choice_modes ?? []).join(", ") || "unknown"],
                  ["Temperature", String(config.native_fc.effective_model_policy.temperature ?? "default")],
                  ["Thinking policy", config.native_fc.effective_model_policy.thinking_policy ?? "none"],
                  ["JSON fallback", config.native_fc.json_simulated_tool_calls_fallback],
                ]}
              />
              <div className="policy-list" aria-label="Native FC model policies">
                {config.allowlists.llm_models.map((model) => {
                  const policy = config.native_fc.model_policies[model];
                  return (
                    <article className="policy-item" key={model}>
                      <strong>{model}</strong>
                      <span>{policy?.recommended_role ?? "candidate"}</span>
                      <small>{(policy?.tool_choice_modes ?? []).join(", ")}</small>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="settings-section">
              <h3>Danger / Read-only</h3>
              <StatusGrid
                rows={[
                  ["Database URL", config.danger_readonly.database_url_status],
                  ["V3 store dir", config.danger_readonly.v3_sandbox_store_dir_status],
                  ["API key", config.danger_readonly.llm_api_key_status],
                ]}
              />
            </section>
          </div>
        )}

        <div className="settings-actions">
          <button type="button" className="secondary-button" onClick={onRefresh} disabled={disabled}>
            <RefreshCw size={16} />
            Refresh status
          </button>
          <button type="button" className="secondary-button" onClick={onReset} disabled={disabled || !config}>
            <RotateCcw size={16} />
            Reset overrides
          </button>
          <button type="button" className="primary-button" onClick={onApply} disabled={disabled || !draft}>
            Apply changes
          </button>
        </div>
      </section>
    </div>
  );
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (checked: boolean) => void }) {
  return (
    <label className="toggle-row">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

function StatusGrid({ rows }: { rows: Array<[string, string]> }) {
  return (
    <div className="status-grid">
      {rows.map(([label, value]) => (
        <div key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}

function TraceControls({
  options,
  onChange,
  disabled,
}: {
  options: V3SandboxDebugTraceOptions;
  onChange: (options: V3SandboxDebugTraceOptions) => void;
  disabled: boolean;
}) {
  function update(next: Partial<V3SandboxDebugTraceOptions>) {
    const merged = { ...options, ...next };
    if (!merged.verbose) {
      onChange(defaultTraceOptions);
      return;
    }
    onChange({
      ...merged,
      include_repair_attempts: true,
      include_node_io: true,
    });
  }

  return (
    <fieldset className="trace-controls" disabled={disabled}>
      <legend>Trace controls</legend>
      <label>
        <input
          type="checkbox"
          checked={options.verbose}
          onChange={(event) =>
            update({
              verbose: event.target.checked,
              include_repair_attempts: event.target.checked,
              include_node_io: event.target.checked,
            })
          }
        />
        Verbose trace
      </label>
      <label>
        <input
          type="checkbox"
          checked={options.include_prompt}
          disabled={!options.verbose || disabled}
          onChange={(event) => update({ include_prompt: event.target.checked })}
        />
        Include prompt
      </label>
      <label>
        <input
          type="checkbox"
          checked={options.include_raw_llm_output}
          disabled={!options.verbose || disabled}
          onChange={(event) => update({ include_raw_llm_output: event.target.checked })}
        />
        Include raw LLM output
      </label>
      <label>
        <input
          type="checkbox"
          checked={options.include_state_diff}
          disabled={!options.verbose || disabled}
          onChange={(event) => update({ include_state_diff: event.target.checked })}
        />
        Include state diff
      </label>
    </fieldset>
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

function CoreMemoryBlocks({ blocks }: { blocks: Record<string, CoreMemoryBlock> | null }) {
  const ordered = ["persona", "human", "product", "sales_strategy", "customer_intelligence"]
    .map((label) => blocks?.[label])
    .filter((block): block is CoreMemoryBlock => Boolean(block));
  if (!ordered.length) {
    return <EmptyState text="No core memory blocks loaded." />;
  }
  return (
    <div className="core-memory-list">
      {ordered.map((block) => (
        <article className="core-memory-block" key={block.label}>
          <div className="row-between">
            <strong>{block.label}</strong>
            <span>
              {block.value.length}/{block.limit}
            </span>
          </div>
          <small>{block.description}</small>
          {block.value ? <p>{block.value}</p> : <span className="empty-state">Empty</span>}
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
            <small>{candidate.id}</small>
            <p>{candidate.ranking_reason || candidate.segment}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function TraceList({
  trace,
  onOpenInspector,
}: {
  trace: V3SandboxTraceEvent[];
  onOpenInspector: (traceId: string | null) => void;
}) {
  if (!trace.length) {
    return <EmptyState text="No trace events yet." />;
  }
  return (
    <div className="trace-list">
      <button type="button" className="secondary-button wide-button" onClick={() => onOpenInspector(trace[trace.length - 1]?.id ?? null)}>
        <PanelTopOpen size={16} />
        Open inspector
      </button>
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
            <p>{event.tool_events.map((tool) => tool.tool_name).join(", ") || event.actions.map((action) => action.type).join(", ") || "no actions"}</p>
            {event.debug_trace ? <p>{event.debug_trace.graph.nodes.join(" -> ")}</p> : null}
            <button type="button" className="secondary-button" onClick={() => onOpenInspector(event.id)}>
              Inspect turn
            </button>
          </article>
        ))}
    </div>
  );
}

function TraceInspector({
  trace,
  selectedTraceId,
  onSelectTrace,
  onClose,
}: {
  trace: V3SandboxTraceEvent[];
  selectedTraceId: string | null;
  onSelectTrace: (traceId: string) => void;
  onClose: () => void;
}) {
  const fallbackTrace = trace[trace.length - 1] ?? null;
  const selectedTrace = trace.find((event) => event.id === selectedTraceId) ?? fallbackTrace;
  const [selectedNode, setSelectedNode] = useState<string | null>(selectedTrace?.debug_trace?.events[0]?.node ?? null);
  const selectedDebugEvent =
    selectedTrace?.debug_trace?.events.find((event) => event.node === selectedNode) ?? selectedTrace?.debug_trace?.events[0] ?? null;

  return (
    <div className="trace-inspector-backdrop" role="dialog" aria-modal="true" aria-label="Trace inspector">
      <section className="trace-inspector">
        <div className="overlay-header">
          <div>
            <div className="eyebrow">LangGraph Workflow</div>
            <h2>Trace Inspector</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close trace inspector">
            <X size={16} />
          </button>
        </div>
        <div className="trace-inspector-grid">
          <aside className="trace-sidebar">
            <h3>Turns</h3>
            {trace
              .slice()
              .reverse()
              .map((event) => (
                <button
                  type="button"
                  className={event.id === selectedTrace?.id ? "trace-turn selected" : "trace-turn"}
                  onClick={() => {
                    onSelectTrace(event.id);
                    setSelectedNode(event.debug_trace?.events[0]?.node ?? null);
                  }}
                  key={event.id}
                >
                  <strong>{event.event_type}</strong>
                  <span>{formatTime(event.created_at)}</span>
                  <span>{event.tool_events.length || event.actions.length} events</span>
                  {event.error ? <span>{event.error.code}</span> : null}
                </button>
              ))}
          </aside>
          <section className="trace-workflow-pane">
            {selectedTrace?.debug_trace ? (
              <>
                <div className="graph-line graph-line-large" aria-label="LangGraph workflow">
                  {selectedTrace.debug_trace.graph.nodes.map((node, index) => (
                    <button
                      type="button"
                      className={node === selectedDebugEvent?.node ? "node-pill selected" : "node-pill"}
                      onClick={() => setSelectedNode(node)}
                      key={node}
                    >
                      {node}
                      {index < selectedTrace.debug_trace!.graph.nodes.length - 1 ? <b>→</b> : null}
                    </button>
                  ))}
                </div>
                <div className="debug-node-list">
                  {selectedTrace.debug_trace.events.map((event) => (
                    <button
                      type="button"
                      className={event.node === selectedDebugEvent?.node ? "debug-node-row selected" : "debug-node-row"}
                      data-testid={`inspector-node-${event.node}`}
                      onClick={() => setSelectedNode(event.node)}
                      key={event.node}
                    >
                      <strong>{event.node}</strong>
                      <span>{event.status}</span>
                      {typeof event.duration_ms === "number" ? <span>{event.duration_ms} ms</span> : null}
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <div className="trace-fallback">
                <EmptyState text="This trace has no verbose debug trace. Runtime metadata and parsed output are still available." />
                {selectedTrace ? (
                  <>
                    <DebugSection title="Runtime metadata" value={selectedTrace.runtime_metadata} />
                    {selectedTrace.tool_events.length ? <ToolEventsList events={selectedTrace.tool_events} /> : null}
                    {selectedTrace.parsed_output ? <DebugSection title="Parsed output" value={selectedTrace.parsed_output} /> : null}
                  </>
                ) : null}
              </div>
            )}
          </section>
          <section className="trace-detail-pane">
            {selectedDebugEvent ? (
              <>
                <div className="trace-detail-title">
                  <h3>{selectedDebugEvent.node}</h3>
                  <span>{selectedDebugEvent.status}</span>
                </div>
                {selectedDebugEvent.input ? <DebugSection title="Input" value={selectedDebugEvent.input} /> : null}
                {selectedDebugEvent.output ? <DebugSection title="Output" value={selectedDebugEvent.output} /> : null}
                {selectedDebugEvent.messages ? <DebugSection title="LLM prompt / messages" value={selectedDebugEvent.messages} defaultOpen={false} /> : null}
                {selectedDebugEvent.raw_output ? <DebugSection title="Raw LLM output" value={selectedDebugEvent.raw_output} defaultOpen={false} /> : null}
                {selectedDebugEvent.repair_attempts ? (
                  <DebugSection title="Repair attempts" value={selectedDebugEvent.repair_attempts} defaultOpen={false} />
                ) : null}
                {selectedDebugEvent.parsed_output ? <DebugSection title="Validated parsed output" value={selectedDebugEvent.parsed_output} /> : null}
                {selectedDebugEvent.action_results ? <DebugSection title="Action apply results" value={selectedDebugEvent.action_results} /> : null}
                {selectedDebugEvent.tool_results ? <DebugSection title="Tool results" value={selectedDebugEvent.tool_results} /> : null}
                {selectedDebugEvent.state_diff ? <DebugSection title="State diff" value={selectedDebugEvent.state_diff} /> : null}
                {selectedDebugEvent.error ? <DebugSection title="Error" value={selectedDebugEvent.error} /> : null}
                {selectedTrace?.tool_events.length ? <ToolEventsList events={selectedTrace.tool_events} /> : null}
              </>
            ) : selectedTrace ? (
              <>
                <DebugSection title="Runtime metadata" value={selectedTrace.runtime_metadata} />
                {selectedTrace.tool_events.length ? <ToolEventsList events={selectedTrace.tool_events} /> : null}
                {selectedTrace.parsed_output ? <DebugSection title="Parsed output" value={selectedTrace.parsed_output} /> : null}
              </>
            ) : (
              <EmptyState text="No trace selected." />
            )}
          </section>
        </div>
      </section>
    </div>
  );
}

function DebugTrace({ trace }: { trace: NonNullable<V3SandboxTraceEvent["debug_trace"]> }) {
  return (
    <div className="debug-trace" data-testid="debug-trace">
      <div className="graph-line" aria-label="LangGraph workflow">
        {trace.graph.nodes.map((node, index) => (
          <span key={node}>
            <code>{node}</code>
            {index < trace.graph.nodes.length - 1 ? <b>→</b> : null}
          </span>
        ))}
      </div>
      {trace.truncated ? <p className="trace-warning">Debug trace was truncated by size limit.</p> : null}
      <div className="debug-node-list">
        {trace.events.map((event, index) => (
          <DebugTraceNode event={event} key={`${event.node}-${index}`} />
        ))}
      </div>
    </div>
  );
}

function DebugTraceNode({ event }: { event: V3SandboxDebugTraceEvent }) {
  const statusClass = event.status === "completed" ? "node-completed" : event.status === "error" ? "node-error" : "node-idle";
  return (
    <details className={`debug-node ${statusClass}`} data-testid={`debug-node-${event.node}`}>
      <summary>
        <strong>{event.node}</strong>
        <span>{event.status}</span>
        {typeof event.duration_ms === "number" ? <span>{event.duration_ms} ms</span> : null}
      </summary>
      <div className="debug-node-body">
        {event.input ? <DebugSection title="Input" value={event.input} /> : null}
        {event.output ? <DebugSection title="Output" value={event.output} /> : null}
        {event.messages ? <DebugSection title="LLM prompt / messages" value={event.messages} defaultOpen={false} /> : null}
        {event.raw_output ? <DebugSection title="Raw LLM output" value={event.raw_output} defaultOpen={false} /> : null}
        {event.repair_attempts ? <DebugSection title="Repair attempts" value={event.repair_attempts} defaultOpen={false} /> : null}
        {event.parsed_output ? <DebugSection title="Validated parsed output" value={event.parsed_output} /> : null}
        {event.action_results ? <DebugSection title="Action apply results" value={event.action_results} /> : null}
        {event.tool_results ? <DebugSection title="Tool results" value={event.tool_results} /> : null}
        {event.state_diff ? <DebugSection title="State diff" value={event.state_diff} /> : null}
        {event.error ? <DebugSection title="Error" value={event.error} /> : null}
      </div>
    </details>
  );
}

function ToolEventsList({ events }: { events: V3SandboxTraceEvent["tool_events"] }) {
  return (
    <section className="tool-events-list" aria-label="Native tool events">
      <h3>Native tool events</h3>
      {events.map((event) => (
        <article className={`tool-event tool-${event.status}`} key={event.id}>
          <div className="row-between">
            <strong>{event.tool_name}</strong>
            <span>{event.status}</span>
          </div>
          <small>{event.block_label ?? "no block"} / {event.tool_call_id}</small>
          {event.tool_name === "send_message" ? <p>final reply source</p> : null}
          {event.error ? <p className="trace-error">{event.error.message}</p> : null}
          <DebugSection title="Arguments" value={event.arguments} defaultOpen={false} />
          <DebugSection title="Result" value={event.result} defaultOpen={false} />
        </article>
      ))}
    </section>
  );
}

function DebugSection({
  title,
  value,
  defaultOpen = true,
}: {
  title: string;
  value: unknown;
  defaultOpen?: boolean;
}) {
  return (
    <details className="debug-section" open={defaultOpen}>
      <summary>{title}</summary>
      <JsonBlock value={value} />
    </details>
  );
}

function JsonBlock({ value }: { value: unknown }) {
  return <pre>{typeof value === "string" ? value : JSON.stringify(value, null, 2)}</pre>;
}

function MemoryTransitions({ inspection }: { inspection: V3SandboxMemoryTransitionsResponse | null }) {
  if (!inspection) {
    return <EmptyState text="No memory transition inspection loaded." />;
  }
  if (!inspection.available) {
    return <EmptyState text="DB inspection unavailable in current store mode." />;
  }
  if (!inspection.transitions.length) {
    return <EmptyState text="No memory transition events yet." />;
  }
  return (
    <div className="transition-list">
      <div className="inspection-counts">
        <span>{inspection.counts.transitions ?? 0} transitions</span>
        <span>{inspection.counts.actions ?? 0} actions</span>
      </div>
      {inspection.transitions
        .slice()
        .reverse()
        .map((transition) => (
          <article className="transition-event" key={transition.id}>
            <div className="row-between">
              <strong>{transition.transition_type}</strong>
              <span>{formatTime(transition.created_at)}</span>
            </div>
            <p>{transition.memory_id}</p>
            <div className="transition-status-row">
              <span>{transition.before_status ?? "new"}</span>
              <span>→</span>
              <span>{transition.after_status ?? "unknown"}</span>
            </div>
            {transition.superseded_by ? <small>superseded by {transition.superseded_by}</small> : null}
            <small>
              {transition.trace_event_id ?? "no trace"} / {transition.turn_id ?? "no turn"} / action{" "}
              {transition.action_index ?? "-"}
            </small>
          </article>
        ))}
    </div>
  );
}

function CoreMemoryTransitions({ inspection }: { inspection: V3SandboxCoreMemoryTransitionsResponse | null }) {
  if (!inspection) {
    return <EmptyState text="No core memory transition inspection loaded." />;
  }
  if (!inspection.available) {
    return <EmptyState text="Core memory DB inspection unavailable in current store mode." />;
  }
  if (!inspection.transitions.length) {
    return <EmptyState text="No core memory transition events yet." />;
  }
  return (
    <div className="transition-list">
      <div className="inspection-counts">
        <span>{inspection.counts.core_memory_block_transitions ?? 0} transitions</span>
        <span>{inspection.counts.traces ?? 0} traces</span>
      </div>
      {inspection.transitions
        .slice()
        .reverse()
        .map((transition) => (
          <article className="transition-event" key={transition.id}>
            <div className="row-between">
              <strong>{transition.transition_type}</strong>
              <span>{formatTime(transition.created_at)}</span>
            </div>
            <p>{transition.block_label}</p>
            <div className="transition-status-row">
              <span>{transition.before_value ? `${transition.before_value.length} chars` : "new"}</span>
              <span>→</span>
              <span>{transition.after_value ? `${transition.after_value.length} chars` : transition.status}</span>
            </div>
            <small>
              {transition.trace_event_id ?? "no trace"} / {transition.turn_id ?? "no turn"} / {transition.tool_event_id ?? "no tool"}
            </small>
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

function yesNo(value: boolean) {
  return value ? "yes" : "no";
}

function enabled(value: boolean) {
  return value ? "enabled" : "disabled";
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}
