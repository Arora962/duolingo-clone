// Thin fetch wrappers around the backend routes.
// The server owns game state and business rules.

import type {
  ChestOpenResult,
  CoursePath,
  Explanation,
  Guidebook,
  HeartsState,
  Leaderboard,
  LegendaryResult,
  LegendaryStart,
  LessonCompleteBody,
  LessonResult,
  LessonStart,
  UserProfile,
} from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/compat";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
      ...init,
    });
  } catch {
    throw new ApiError(
      0,
      `Can't reach the API at ${BASE_URL}. Is the backend running?`,
    );
  }

  if (!response.ok) {
    let message =
      response.statusText ||
      `Request failed (${response.status})`;

    try {
      const body = await response.json();

      if (typeof body?.detail === "string") {
        message = body.detail;
      } else if (
        body?.detail &&
        typeof body.detail === "object" &&
        typeof body.detail.message === "string"
      ) {
        // FastAPI's structured application errors use:
        // { detail: { code, message, ... } }
        message = body.detail.message;
      }
    } catch {
      // Non-JSON error body — keep the HTTP status text.
    }

    throw new ApiError(
      response.status,
      message,
    );
  }

  return (await response.json()) as T;
}

export const api = {
  me: () =>
    request<UserProfile>("/api/user/me"),

  coursePath: () =>
    request<CoursePath>("/api/course/path"),

  jumpToUnit: (unitId: number) =>
    request<CoursePath>(
      `/api/course/units/${unitId}/jump`,
      {
        method: "POST",
      },
    ),

  openChest: (skillId: number) =>
    request<ChestOpenResult>(
      `/api/course/chest/${skillId}/open`,
      {
        method: "POST",
      },
    ),

  guidebook: (unitId: number) =>
    request<Guidebook>(
      `/api/course/units/${unitId}/guidebook`,
    ),

  startLesson: (skillId: number) =>
    request<LessonStart>(
      `/api/lesson/${skillId}/start`,
    ),

  /**
   * Persist an incorrect answer immediately.
   *
   * This is important because the learner can hit zero hearts and leave the
   * lesson before the lesson-complete endpoint is called.
   */
  recordMistake: (
    attemptId: number,
    exerciseId: number,
  ) =>
    request<HeartsState>(
      `/api/lesson/${attemptId}/mistake`,
      {
        method: "POST",
        body: JSON.stringify({
          exercise_id: exerciseId,
        }),
      },
    ),

  completeLesson: (
    lessonId: number,
    body: LessonCompleteBody,
  ) =>
    request<LessonResult>(
      `/api/lesson/${lessonId}/complete`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),

  startLegendary: (skillId: number) =>
    request<LegendaryStart>(
      `/api/lesson/${skillId}/legendary`,
    ),

  completeLegendary: (
    skillId: number,
    body: LessonCompleteBody,
  ) =>
    request<LegendaryResult>(
      `/api/lesson/${skillId}/legendary/complete`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),

  refillHearts: () =>
    request<HeartsState>(
      "/api/hearts/refill",
      {
        method: "POST",
      },
    ),

  leaderboard: () =>
    request<Leaderboard>(
      "/api/leaderboard",
    ),

  explain: (body: {
    question: string;
    correct_answer: string;
    user_answer?: string;
  }) =>
    request<Explanation>(
      "/api/exercise/explain",
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),
};