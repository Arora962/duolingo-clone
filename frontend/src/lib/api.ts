import type {
  AnswerPayload,
  AnswerResult,
  Clock,
  CompleteResult,
  HeartsResponse,
  LeaderboardResponse,
  Me,
  PathResponse,
  ProfileResponse,
  RefillMethod,
  RefillResponse,
  Settings,
  StartLessonResponse,
  TreasureResponse,
} from "~/lib/types";

const ORIGIN = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/$/, "");
const BASE = `${ORIGIN}/api`;

/** Backend errors look like {detail: {code, message, ...extra}}. */
export class ApiError extends Error {
  status: number;
  code: string;
  data: Record<string, unknown>;

  constructor(status: number, code: string, message: string, data = {}) {
    super(message);
    this.status = status;
    this.code = code;
    this.data = data;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Cannot reach the server.");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    if (detail && typeof detail === "object" && "code" in detail) {
      const { code, message, ...rest } = detail;
      throw new ApiError(res.status, code, message ?? code, rest);
    }
    throw new ApiError(res.status, "HTTP_ERROR", `Request failed (${res.status})`);
  }
  return (await res.json()) as T;
}

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
  });

export const api = {
  me: () => request<Me>("/me"),
  path: () => request<PathResponse | null>("/path"),
  profile: () => request<ProfileResponse>("/profile"),
  leaderboard: () => request<LeaderboardResponse>("/leaderboard"),

  settings: () => request<Settings>("/settings"),
  updateSettings: (patch: Partial<Settings>) =>
    request<Settings>("/settings", {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),

  hearts: () => request<HeartsResponse>("/hearts"),
  refillHearts: (method: RefillMethod) =>
    post<RefillResponse>("/hearts/refill", { method }),

  startLesson: (lessonId: number) =>
    post<StartLessonResponse>(`/lessons/${lessonId}/start`),
  answer: (attemptId: number, payload: AnswerPayload) =>
    post<AnswerResult>(`/attempts/${attemptId}/answer`, payload),
  complete: (attemptId: number) =>
    post<CompleteResult>(`/attempts/${attemptId}/complete`),
  abandon: (attemptId: number) =>
    post<{ status: "ABANDONED" }>(`/attempts/${attemptId}/abandon`),
  claimTreasure: (skillId: number) =>
    post<TreasureResponse>(`/skills/${skillId}/claim-treasure`),

  // Dev-only simulated clock (only exists when ENABLE_DEV_ENDPOINTS=true)
  clock: () => request<Clock>("/dev/clock"),
  advanceClock: (days = 1) => post<Clock>("/dev/clock/advance", { days }),
  resetClock: () => post<Clock>("/dev/clock/reset"),
};