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

export async function createSession(title = "V3 Sales Agent Lab"): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession }>("/api/v3/sandbox/sessions", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
  return payload.session;
}

export async function createTurn(sessionId: string, content: string): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession }>(`/api/v3/sandbox/sessions/${sessionId}/turns`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
  return payload.session;
}

export async function getSession(sessionId: string): Promise<V3SandboxSession> {
  const payload = await requestJson<{ session: V3SandboxSession }>(`/api/v3/sandbox/sessions/${sessionId}`);
  return payload.session;
}

export async function getTrace(sessionId: string): Promise<V3SandboxTraceEvent[]> {
  const payload = await requestJson<{ trace: V3SandboxTraceEvent[] }>(`/api/v3/sandbox/sessions/${sessionId}/trace`);
  return payload.trace;
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
