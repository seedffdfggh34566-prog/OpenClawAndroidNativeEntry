export type CoreMemoryBlock = {
  label: "persona" | "human" | "product" | "sales_strategy" | "customer_intelligence";
  description: string;
  value: string;
  limit: number;
  read_only: boolean;
  updated_at: string;
};

export type CoreMemoryToolEvent = {
  id: string;
  tool_call_id: string;
  tool_name: string;
  arguments: Record<string, unknown>;
  status: "applied" | "error";
  result: Record<string, unknown>;
  error: { code: string; message: string } | null;
  block_label: string | null;
  before_value: string | null;
  after_value: string | null;
  created_at: string;
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
  tool_results?: unknown;
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
  tool_events: CoreMemoryToolEvent[];
  parsed_output: Record<string, unknown> | null;
  debug_trace: V3SandboxDebugTrace | null;
  error: { code: string; message: string } | null;
  created_at: string;
};

export type V3SandboxSession = {
  id: string;
  title: string;
  core_memory_blocks: Record<string, CoreMemoryBlock>;
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

export type V3SandboxCoreMemoryTransition = {
  id: string;
  transition_type: string;
  block_label: string;
  status: "applied" | "error" | string;
  trace_event_id: string | null;
  turn_id: string | null;
  tool_event_id: string | null;
  tool_call_id: string | null;
  before_value: string | null;
  after_value: string | null;
  payload: Record<string, unknown>;
  created_at: string;
};

export type V3SandboxCoreMemoryTransitionsResponse = {
  session_id: string;
  available: boolean;
  reason: string | null;
  store: V3SandboxStoreStatus;
  counts: Record<string, number>;
  transitions: V3SandboxCoreMemoryTransition[];
};

export type V3SandboxRuntimeConfig = {
  backend_status: {
    store: V3SandboxStoreStatus;
    llm_provider: string;
    llm_model: string;
    llm_api_key_status: "configured" | "missing";
    llm_timeout_seconds: number;
    native_fc_supported: boolean;
    native_fc_recommended_role: string;
    memory_runtime: string;
    native_function_calling: boolean;
    langfuse_enabled: boolean;
    dev_llm_trace_enabled: boolean;
  };
  runtime_config: {
    llm_model: string;
    llm_timeout_seconds: number;
    max_steps: number;
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
    max_steps: { min: number; max: number; default: number };
    trace_max_bytes: number[];
  };
  native_fc: {
    default_model: string;
    effective_model_policy: V3SandboxNativeFcModelPolicy;
    model_policies: Record<string, V3SandboxNativeFcModelPolicy>;
    json_simulated_tool_calls_fallback: string;
  };
  memory_runtime: {
    mode: string;
    core_memory_blocks: string[];
    tools: string[];
  };
};

export type V3SandboxRuntimeConfigPatch = Partial<V3SandboxRuntimeConfig["runtime_config"]>;

export type V3SandboxNativeFcModelPolicy = {
  native_tool_calling?: boolean;
  recommended_role?: string;
  temperature?: number | string;
  thinking_policy?: string;
  tool_choice_modes?: string[];
  notes?: string;
};

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

export async function getCoreMemoryTransitions(sessionId: string): Promise<V3SandboxCoreMemoryTransitionsResponse> {
  return requestJson(`/api/v3/sandbox/sessions/${sessionId}/core-memory-transitions`);
}

export type SmokeTurn = {
  turn: number;
  user_preview: string;
  duration_seconds: number;
  assistant_preview: string;
  tool_calls: string[];
  memory_block_lengths: Record<string, number>;
  memory_block_snapshots: Record<string, string>;
  context_summary_present: boolean;
  summary_recursion_count: number;
  early_return_reason: string | null;
  token_count: number;
  prompt_warning: boolean;
  error: string | null;
};

export type SmokeStatusResponse = {
  running: boolean;
  total_turns: number;
  completed_turns: number;
  turns: SmokeTurn[];
};

export async function getSmokeStatus(): Promise<SmokeStatusResponse> {
  return requestJson(`/api/v3/sandbox/smoke-status`);
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
