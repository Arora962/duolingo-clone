# Duolingo Clone Backend

FastAPI + SQLAlchemy 2.0 + SQLite backend for the Duolingo-style learning application.

## Setup

From the `backend/` directory:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
```

The application uses SQLite by default and creates `duolingo.db` in the backend directory.

## Seed the database

Run the idempotent seed command:

```bash
python -m app.seed
```

The seeded learner has:

- 110 XP
- a 3-day current streak
- 4 hearts from one `LOST` heart event
- 11 completed lesson attempts worth 10 XP each
- 11 attempts are distributed across 2026-10-04, 2026-10-05, and 2026-10-06

Running the seed repeatedly does not duplicate the seeded rows or learner history.

## Run the server

```bash
uvicorn app.main:app --reload
```

The API is available under `/api`.

## Run tests

```bash
pytest
```

The test suite uses an isolated in-memory SQLite database with foreign-key enforcement enabled.

## Environment variables

### `ENABLE_DEV_ENDPOINTS`

Controls whether the simulated-clock development router is registered.

Default:

```text
true
```

Disable development endpoints in a production-like environment with:

```text
ENABLE_DEV_ENDPOINTS=false
```

### `DATABASE_URL`

Optional SQLAlchemy database URL. If omitted, the backend uses the local SQLite database:

```text
sqlite:///duolingo.db
```

### `AUTO_SEED`

Optional startup seeding switch. Default is `false`.

```text
AUTO_SEED=true
```

### `CORS_ORIGINS`

Comma-separated frontend origins. The default allows the common local React development URLs:

```text
http://localhost:3000,http://127.0.0.1:3000
```

## Endpoint list

### Learner

- `GET /api/me`
- `GET /api/profile`
- `GET /api/settings`
- `PATCH /api/settings`

### Learning path

- `GET /api/path`

### Lessons and attempts

- `POST /api/lessons/{lesson_id}/start`
- `POST /api/attempts/{attempt_id}/answer`
- `POST /api/attempts/{attempt_id}/complete`
- `POST /api/attempts/{attempt_id}/abandon`
- `POST /api/skills/{skill_id}/claim-treasure`

### Hearts

- `GET /api/hearts`
- `POST /api/hearts/refill`

### Leaderboard

- `GET /api/leaderboard`

### Development clock

These routes exist only when `ENABLE_DEV_ENDPOINTS=true`:

- `GET /api/dev/clock`
- `POST /api/dev/clock/advance`
- `POST /api/dev/clock/reset`

### Health

- `GET /api/health`

## Architecture

The backend follows a thin-router architecture: **routers → services → models**. Routers handle HTTP concerns, dependency injection, request validation, response-model serialization, and transaction commits. Services contain lesson lifecycle, answer evaluation, hearts, statistics, achievements, leaderboard, and path logic. SQLAlchemy models define the frozen 15-table relational schema and its constraints, indexes, relationships, and delete behavior. Pydantic schemas define the public request and response contracts consumed by the frontend.

## Database schema

The backend intentionally preserves the frozen 15-table SQLite schema:

| Table | Purpose |
| --- | --- |
| `courses` | Available language courses |
| `units` | Ordered course units |
| `skills` | Ordered skills within units |
| `lessons` | Scored lessons within skills |
| `exercises` | Lesson questions |
| `exercise_options` | Choice, word-bank, and matching options |
| `exercise_accepted_answers` | Accepted typed/translated answers |
| `users` | Learner accounts and course selection |
| `user_settings` | Persistent learner preferences |
| `lesson_attempts` | Lesson attempt lifecycle and XP |
| `attempt_answers` | Submitted exercise answers |
| `heart_events` | Heart gains/losses and refill history |
| `achievements` | Achievement definitions |
| `user_achievements` | Learner achievement progress/unlocks |
| `system_settings` | Simulated-clock and other system settings |

Foreign keys, uniqueness constraints, check constraints, indexes, and cascade/set-null behavior are defined in the SQLAlchemy models. The seed is idempotent and does not create duplicate learner history.

## Simulated clock

The application uses naive UTC timestamps consistently. `app.clock.now_utc()` reads the `time_offset_days` value from `system_settings` and returns real UTC time plus that simulated day offset. The development clock routes can advance or reset the offset without changing stored lesson history. Streaks, daily XP, weekly leaderboard periods, and heart regeneration therefore use the simulated clock while database timestamps remain ordinary naive UTC values. This makes date-dependent behavior deterministic and testable without waiting for real calendar days.

## Business rules

- Maximum hearts: `5`.
- One heart regenerates every `30` minutes while below the maximum.
- Gem refill costs `100` gems and fills all missing hearts.
- Practice refill adds one heart.
- Treasure completion awards `30` gems and `0` XP.
- Practice lessons use a `180` second time limit.
- XP is derived from completed non-treasure lesson attempts.
- Current streak is derived from consecutive dates with completed non-treasure lessons.
- Skill crowns equal the number of completed lessons in that skill.
