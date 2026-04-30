export type MemoryStatus = "observed" | "inferred" | "hypothesis" | "confirmed" | "rejected" | "superseded";

export type MemoryItem = {
  id: string;
  status: MemoryStatus;
  content: string;
  source: string;
  evidence: string[];
  confidence: number;
  supersedes: string[];
  superseded_by: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type SandboxWorkingState = {
  product_understanding: string[];
  sales_strategy: string[];
  open_questions: string[];
  current_hypotheses: string[];
  correction_summary: string[];
  updated_at: string;
};

export type CustomerCandidateDraft = {
  id: string;
  name: string;
  segment: string;
  target_roles: string[];
  ranking_reason: string;
  score: number;
  validation_signals: string[];
};

export type CustomerIntelligenceDraft = {
  target_industries: string[];
  target_roles: string[];
  candidates: CustomerCandidateDraft[];
  ranking_reasons: string[];
  scoring_draft: Record<string, number>;
  validation_signals: string[];
  updated_at: string;
};

export type AgentAction = {
  type: "write_memory" | "update_memory_status" | "update_working_state" | "update_customer_intelligence" | "no_op";
  payload: Record<string, unknown>;
};

export type V3SandboxDebugTraceOptions = {
  verbose: boolean;
  include_prompt: boolean;
  include_raw_llm_output: boolean;
  include_repair_attempts: boolean;
  include_node_io: boolean;
  include_state_diff: boolean;
  max_bytes?: number;
};

export type V3SandboxDebugTraceEvent = {
  node: string;
  status: string;
  duration_ms?: number;
  input?: unknown;
  output?: unknown;
  messages?: unknown;
  raw_output?: unknown;
  repair_attempts?: unknown;
  parsed_output?: unknown;
  action_results?: unknown;
  state_diff?: unknown;
  error?: unknown;
};

export type V3SandboxDebugTrace = {
  version: string;
  truncated: boolean;
  options: Record<string, unknown>;
  graph: {
    nodes: string[];
    edges: string[][];
  };
  events: V3SandboxDebugTraceEvent[];
};

export type V3SandboxMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type V3SandboxTraceEvent = {
  id: string;
  session_id: string;
  turn_id: string;
  event_type: string;
  runtime_metadata: Record<string, unknown>;
  actions: AgentAction[];
  parsed_output: Record<string, unknown> | null;
  debug_trace: V3SandboxDebugTrace | null;
  error: { code: string; message: string } | null;
  created_at: string;
};

export type V3SandboxSession = {
  id: string;
  title: string;
  memory_items: Record<string, MemoryItem>;
  working_state: SandboxWorkingState;
  customer_intelligence: CustomerIntelligenceDraft;
  messages: V3SandboxMessage[];
  trace: V3SandboxTraceEvent[];
  created_at: string;
  updated_at: string;
};

export type V3SandboxReplayReport = {
  status: "completed" | "failed";
  source_session_id: string;
  replay_session_id: string;
  replayed_turns: number;
  failed_turn_index: number | null;
  error: { code: string; message: string } | null;
};

export type V3SandboxStoreStatus = {
  backend: "memory" | "json" | "database";
  database_enabled: boolean;
  json_enabled: boolean;
  transition_events_supported: boolean;
};

export type V3SandboxMemoryTransition = {
  id: string;
  transition_type: "write_memory" | "update_memory_status" | "supersede_memory" | string;
  memory_id: string;
  before_status: MemoryStatus | null;
  after_status: MemoryStatus | null;
  superseded_by: string | null;
  trace_event_id: string | null;
  turn_id: string | null;
  action_index: number | null;
  payload: Record<string, unknown>;
  created_at: string;
};

export type V3SandboxMemoryTransitionsResponse = {
  session_id: string;
  available: boolean;
  reason: string | null;
  store: V3SandboxStoreStatus;
  counts: Record<string, number>;
  transitions: V3SandboxMemoryTransition[];
};

export type V3SandboxRuntimeConfig = {
  backend_status: {
    store: V3SandboxStoreStatus;
    llm_provider: string;
    llm_model: string;
    llm_api_key_status: "configured" | "missing";
    llm_timeout_seconds: number;
    langfuse_enabled: boolean;
    dev_llm_trace_enabled: boolean;
  };
  runtime_config: {
    llm_model: string;
    llm_timeout_seconds: number;
    default_debug_trace: boolean;
    default_include_prompt: boolean;
    default_include_raw_llm_output: boolean;
    default_include_state_diff: boolean;
    replay_debug_trace: boolean;
    trace_max_bytes: number;
  };
  danger_readonly: {
    database_url_status: "configured" | "default_sqlite" | string;
    v3_sandbox_store_dir_status: "configured" | "not_configured" | string;
    llm_api_key_status: "configured" | "missing";
  };
  overrides: Record<string, unknown>;
  allowlists: {
    llm_models: string[];
    llm_timeout_seconds: number[];
    trace_max_bytes: number[];
  };
};

export type V3SandboxRuntimeConfigPatch = Partial<V3SandboxRuntimeConfig["runtime_config"]>;

type ApiErrorPayload = {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
};

export class ApiError extends Error {
  code: string;
  status: number;
  details: Record<string, unknown>;

  constructor(status: number, payload: ApiErrorPayload) {
    super(payload.error.message);
    this.name = "ApiError";
    this.status = status;
    this.code = payload.error.code;
    this.details = payload.error.details;
  }
}

export async function getHealth(): Promise<{ status: string }> {
  return requestJson("/api/health");
}

export async function getStoreStatus(): Promise<V3SandboxStoreStatus> {
  return requestJson("/api/v3/sandbox/store");
}

export async function getRuntimeConfig(): Promise<V3SandboxRuntimeConfig> {
  return requestJson("/api/v3/sandbox/runtime-config");
}

export async function updateRuntimeConfig(payload: V3SandboxRuntimeConfigPatch): Promise<V3SandboxRuntimeConfig> {
  return requestJson("/api/v3/sandbox/runtime-config", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function resetRuntimeConfig(): Promise<V3SandboxRuntimeConfig> {
  return requestJson("/api/v3/sandbox/runtime-config/reset", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function createSession(title = "V3 Sales Agent Lab"): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession }>("/api/v3/sandbox/sessions", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
  return payload.session;
}

export async function createDemoSeed(scenario = "sales_training_correction"): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession; scenario: string }>("/api/v3/sandbox/demo-seeds", {
    method: "POST",
    body: JSON.stringify({ scenario }),
  });
  return payload.session;
}

export async function createTurn(
  sessionId: string,
  content: string,
  debugTrace?: Partial<V3SandboxDebugTraceOptions>,
): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession }>(`/api/v3/sandbox/sessions/${sessionId}/turns`, {
    method: "POST",
    body: JSON.stringify({ content, ...(debugTrace ? { debug_trace: debugTrace } : {}) }),
  });
  return payload.session;
}

export async function replaySession(
  sessionId: string,
): Promise<{ session: V3SandboxSession; replay: V3SandboxReplayReport }> {
  return requestJson(`/api/v3/sandbox/sessions/${sessionId}/replay`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function getSession(sessionId: string): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession }>(`/api/v3/sandbox/sessions/${sessionId}`);
  return payload.session;
}

export async function getTrace(sessionId: string): Promise<V3SandboxTraceEvent[]> {
  const payload = await requestJson<{ trace: V3SandboxTraceEvent[] }>(`/api/v3/sandbox/sessions/${sessionId}/trace`);
  return payload.trace;
}

export async function getMemoryTransitions(sessionId: string): Promise<V3SandboxMemoryTransitionsResponse> {
  return requestJson(`/api/v3/sandbox/sessions/${sessionId}/memory-transitions`);
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  const payload = (await response.json()) as T | ApiErrorPayload;
  if (!response.ok) {
    throw new ApiError(response.status, payload as ApiErrorPayload);
  }
  return payload as T;
}
