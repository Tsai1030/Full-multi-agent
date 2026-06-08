import type {
  AnalysisRequest,
  AnalysisResponse,
  ApiErrorDetail,
  BirthData,
  ChartProfile,
  ChatMessage,
  ChatSession,
  ProfileCreate,
  SubscriptionInfo,
  SubscriptionPlan,
  TokenCheckResult,
  TokenResponse,
  TokenTransaction,
  User,
  ZiweiChart,
} from "@/types";
import { API_BASE } from "@/lib/constants";

export class ApiError extends Error {
  status: number;
  detail: ApiErrorDetail | null;

  constructor(status: number, message: string, detail?: ApiErrorDetail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail ?? null;
  }

  get isFeatureLocked(): boolean {
    return this.status === 403 && this.detail?.error === "feature_locked";
  }

  get isInsufficientTokens(): boolean {
    return this.status === 402 && this.detail?.error === "insufficient_tokens";
  }

  get isProfileLimit(): boolean {
    return this.status === 403 && this.detail?.error === "profile_limit";
  }
}

// Access token 存記憶體（不落地），refresh token 走 httpOnly cookie 由瀏覽器自動帶上
let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string> | undefined) };
  if (init.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "object" ? body.detail as ApiErrorDetail : null;
    const message = detail?.message || (typeof body.detail === "string" ? body.detail : `HTTP ${res.status}`);
    throw new ApiError(res.status, message, detail ?? undefined);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function analyzeChart(
  req: AnalysisRequest,
  signal?: AbortSignal
): Promise<AnalysisResponse> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers,
    credentials: "include",
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "object" ? body.detail as ApiErrorDetail : null;
    const message = detail?.message || (typeof body.detail === "string" ? body.detail : `HTTP ${res.status}`);
    throw new ApiError(res.status, message, detail ?? undefined);
  }

  return res.json();
}

export async function getSystemStatus() {
  const res = await fetch(`${API_BASE}/api/status`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

// ── Auth ─────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (email: string, password: string, displayName: string, birthData: BirthData, chart: ZiweiChart) =>
    request<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        display_name: displayName,
        birth_data: birthData,
        chart,
      }),
    }),

  google: (credential: string) =>
    request<TokenResponse>("/api/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential }),
    }),

  /** 用 httpOnly refresh cookie 換新 access token；成功則存入記憶體並回傳 true */
  async refresh(): Promise<boolean> {
    try {
      const res = await request<TokenResponse>("/api/auth/refresh", { method: "POST" });
      setAccessToken(res.access_token);
      return true;
    } catch {
      return false;
    }
  },

  me: () => request<User>("/api/auth/me"),

  logout: () => request<{ success: boolean }>("/api/auth/logout", { method: "POST" }),
};

// ── Chart Profile ────────────────────────────────────────────
export const profileApi = {
  list: () => request<ChartProfile[]>("/api/profiles"),
  get: (id: string) => request<ChartProfile>(`/api/profiles/${id}`),
  create: (data: ProfileCreate) =>
    request<ChartProfile>("/api/profiles", { method: "POST", body: JSON.stringify(data) }),
  remove: (id: string) => request<void>(`/api/profiles/${id}`, { method: "DELETE" }),
};

// ── Chat（與大師對談）────────────────────────────────────────
export const chatApi = {
  listSessions: (profileId: string) =>
    request<ChatSession[]>(`/api/chat/sessions?profile_id=${encodeURIComponent(profileId)}`),

  createSession: (profileId: string, title?: string) =>
    request<ChatSession>("/api/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, title }),
    }),

  messages: (sessionId: string) => request<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`),

  send: (sessionId: string, content: string) =>
    request<ChatMessage>(`/api/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  /** SSE stream for master reply; each chunk is passed to onDelta, returns final message id/created_at */
  async stream(
    sessionId: string,
    content: string,
    onDelta: (delta: string) => void
  ): Promise<{ id: string; created_at: string }> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

    const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}/messages/stream`, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify({ content }),
    });

    if (!res.ok || !res.body) {
      const body = await res.json().catch(() => ({}));
      throw new ApiError(res.status, body.detail || `HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let result: { id: string; created_at: string } | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";
      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;
        const json = line.slice(5).trim();
        if (!json) continue;

        const payload = JSON.parse(json) as { delta?: string; error?: string; done?: boolean; id?: string; created_at?: string };
        if (payload.delta) onDelta(payload.delta);
        else if (payload.error) throw new ApiError(500, payload.error);
        else if (payload.done && payload.id && payload.created_at) {
          result = { id: payload.id, created_at: payload.created_at };
        }
      }
    }

    if (!result) throw new ApiError(500, "大師暫時無法回應，請稍後再試");
    return result;
  },
};

// ── Subscription ────────────────────────────────────────────

export const subscriptionApi = {
  plans: () => request<SubscriptionPlan[]>("/api/subscription/plans"),
  me: () => request<SubscriptionInfo>("/api/subscription/me"),
  subscribe: (planName: string) =>
    request<{ message: string; plan: string }>("/api/subscription/subscribe", {
      method: "POST",
      body: JSON.stringify({ plan_name: planName }),
    }),
  cancel: () =>
    request<{ message: string; period_end: string }>("/api/subscription/cancel", {
      method: "POST",
    }),
};

// ── Tokens ──────────────────────────────────────────────────

export const tokenApi = {
  balance: () =>
    request<{ balance: number; period_start: string | null; period_end: string | null }>("/api/tokens/balance"),
  history: (page = 1) =>
    request<TokenTransaction[]>(`/api/tokens/history?page=${page}`),
  check: (action: string) =>
    request<TokenCheckResult>("/api/tokens/check", {
      method: "POST",
      body: JSON.stringify({ action }),
    }),
};

// ── Fortune (ephemeral chat + compatibility) ────────────────

export const fortuneApi = {
  async stream(
    params: {
      domain: string;
      analysis_context: string;
      chart_text: string;
      messages: Array<{ role: string; content: string }>;
      user_message: string;
    },
    onDelta: (delta: string) => void,
  ): Promise<void> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

    const res = await fetch(`${API_BASE}/api/fortune/stream`, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify(params),
    });

    if (!res.ok || !res.body) {
      const body = await res.json().catch(() => ({}));
      const detail = typeof body.detail === "object" ? body.detail as ApiErrorDetail : null;
      const message = detail?.message || (typeof body.detail === "string" ? body.detail : `HTTP ${res.status}`);
      throw new ApiError(res.status, message, detail ?? undefined);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";
      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;
        const json = line.slice(5).trim();
        if (!json) continue;

        const payload = JSON.parse(json) as { delta?: string; error?: string; done?: boolean };
        if (payload.delta) onDelta(payload.delta);
        else if (payload.error) throw new ApiError(500, payload.error);
      }
    }
  },

  compatibility: (data: {
    birth_data_1: BirthData;
    birth_data_2: BirthData;
    chart_1: ZiweiChart;
    chart_2: ZiweiChart;
    user_question?: string;
  }) =>
    request<AnalysisResponse>("/api/fortune/compatibility", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
