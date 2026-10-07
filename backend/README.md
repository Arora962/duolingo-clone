# Backend

FastAPI + SQLAlchemy 2.0 + SQLite service for the Duolingo clone. It owns all game state and rules: path progression, lesson attempts, XP, streaks, hearts, achievements and the leaderboard.

Back to the [project overview](../README.md). For the full database design, see [`SCHEMA_DESIGN_FINAL.md`](SCHEMA_DESIGN_FINAL.md).

## Contents

- [Setup](#setup)
- [Architecture](#architecture)
- [`/api` and `/compat`: two API surfaces](#api-and-compat-two-api-surfaces)
- [`/api` reference](#api-reference-native-contract)
- [`/compat` reference](#compat-reference-frontend-adapter)
- [Business rules](#business-rules)
- [Simulated clock](#simulated-clock)
- [Database](#database)
- [Configuration](#configuration)
- [Tests](#tests)

## Setup

Requires Python 3.11+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python -m app.seed                 # idempotent; creates duolingo.db
uvicorn app.main:app --reload      # http://localhost:8000
```

- Interactive docs: http://localhost:8000/docs
- Health check: `GET /api/health`
- To start from a clean database, delete `duolingo.db` and run the seed again.
- To seed automatically on startup instead, set `AUTO_SEED=true`.

### What the seed creates

| Item | Detail |
| --- | --- |
| Course | Spanish for English speakers: 2 units, 8 skills (4 lesson skills × 2 lessons, 2 treasure chests, 2 practice nodes) |
| Exercises | 40, with 8 of each type: multiple choice, word-bank translate, match pairs, fill in the blank, type answer |
| Learner | `learner`: 110 XP, 3-day streak ending today, 4 hearts (one `LOST` event) |
| Rivals | `bot1`–`bot10` for the leaderboard |
| Achievements | `STREAK_3`, `STREAK_7`, `XP_100`, `XP_500`, `FIRST_LESSON`, `PERFECT_LESSON` |

Running the seed again never duplicates content or learner history.

## Architecture

```
app/
├── main.py          app factory, CORS, router mounting, lifespan (create tables, optional seed)
├── config.py        environment-backed settings
├── constants.py     game constants (max hearts, regen time, gem costs, ...)
├── database.py      engine, session, naming convention, SQLite foreign-key pragma
├── deps.py          get_current_user (the single replaceable "auth" hook)
├── clock.py         simulated clock (now_utc / today)
├── errors.py        api_error(): structured errors
├── enums.py         shared enums
├── models/          SQLAlchemy models: content, learner, gamification
├── schemas/         Pydantic request/response contracts (one module per router + compat)
├── routers/         HTTP layer: me, path, lessons, hearts, leaderboard, dev, compat
├── services/        business logic: lessons, answers, hearts, stats, path, achievements,
│                    leaderboard, compat
├── seed.py          idempotent seeding command
└── seed_data.py     plain-Python course content
```

The design is a thin-router layering of **routers → services → models**:

- **Routers** handle HTTP only: dependency injection, validation, response-model serialisation and the transaction commit.
- **Services** hold the rules (lesson lifecycle, answer checking, hearts, streaks, XP, achievements, path locking, leaderboard).
- **Models** define the schema, constraints and relationships.
- **Schemas** are the public contract the clients consume.

The learner comes from `get_current_user`, which returns the seeded `learner`. Replacing real authentication means changing only that dependency.

## `/api` and `/compat`: two API surfaces

The backend serves two contracts. Both call the **same services and write to the same 15-table database**, so progress made through one is visible through the other.

| | `/api` (native) | `/compat` (frontend adapter) |
| --- | --- | --- |
| Purpose | A clean, general API design | Exactly the shapes the Duolingo-style UI expects |
| Router | `routers/me, path, lessons, hearts, leaderboard, dev` | `routers/compat.py` |
| Logic | `services/*` | `services/compat.py`, which delegates to `services/*` |
| Exercise payloads | Answers are hidden; only options and tiles are sent | Answers are included so the browser can grade instantly |
| Grading | **Server-side**, one `POST /answer` per exercise | **Client-side**, with hearts and totals reconciled on the server |
| Identifiers | `lesson_id` starts an attempt; `attempt_id` is used afterwards | `skill_id` starts a lesson; the returned `lesson_id` is actually the **attempt id** |
| Field names | `total_xp`, `current_streak`, `display_name` | `xp_total`, `streak_count`, `name` |
| Used by | API clients, tests, Swagger | The Next.js frontend (default base URL) |

### Why `/compat` exists

The frontend was built against its own contract: nested unit/skill nodes, exercises whose payload already contains the correct answer, a single "complete" call carrying counts, and so on. The native API is stricter. It never leaks answers and records each answer individually.

Rather than distort the native design or change the schema, `/compat` is an **adapter layer**:

- it translates schema rows into the UI's payload shapes (for example, `exercise_options` rows become `{question, options, correct}`);
- it reuses the native services for every state change, so XP, streak and heart rules are defined once;
- it **adds no tables and no migrations**.

### How the two prefixes are mounted

The prefix is applied in `main.py`, and the compat router's own paths already begin with `/api/...`:

```python
app.include_router(me.router,          prefix="/api")      # /api/me, /api/profile, ...
app.include_router(compat.router,      prefix="/compat")   # /compat/api/user/me, ...
```

So the compat URLs are `/compat/api/...`. The frontend's client keeps relative paths such as `/api/user/me` and sets its base URL to `http://localhost:8000/compat`. The final request is `/compat/api/user/me`.

### The lesson flow in each

**Native `/api`:**

1. `POST /api/lessons/{lesson_id}/start` creates an `IN_PROGRESS` attempt and returns exercises without answers.
2. `POST /api/attempts/{attempt_id}/answer` is called once per exercise. The server grades it, records an `attempt_answers` row and, if wrong, writes a `LOST` heart event.
3. `POST /api/attempts/{attempt_id}/complete` awards XP, updates the streak, evaluates achievements and unlocks the next skill.
4. `POST /api/attempts/{attempt_id}/abandon` abandons an active attempt.

**Compat `/compat/api`:**

1. `GET /lesson/{skill_id}/start` picks the next unfinished lesson in the skill, creates the attempt and returns exercises **with answers**.
2. `POST /lesson/{attempt_id}/mistake` is called **immediately on each wrong answer**, so heart loss survives a refresh or an exit at zero hearts. It records the wrong answer and a `LOST` event, and returns the hearts left.
3. `POST /lesson/{attempt_id}/complete` takes `{correct_count, mistake_count}`. The server checks that the counts add up to the lesson's exercise count and that they are consistent with mistakes already saved. It writes only the *missing* mistakes (so no heart is charged twice) and then calls the native `complete()`.

The compat flow still protects the invariants. A caller cannot finish a lesson by spending the last heart, a finished attempt can't be completed twice, and impossible counts are rejected with `422 INVALID_LESSON_RESULT`.

## `/api` reference (native contract)

All routes are under `/api`. Responses are JSON; errors use `{"detail": {"code": "...", "message": "..."}}`.

| Area | Method and path | Description |
| --- | --- | --- |
| Learner | `GET /api/me` | Summary: XP, streak, hearts, gems, daily goal progress, current course |
| | `GET /api/profile` | Profile stats and achievements |
| | `GET /api/settings` | Learner settings |
| | `PATCH /api/settings` | Update settings (daily goal must be 10, 20, 30 or 50) |
| Path | `GET /api/path` | Units and skills with `LOCKED` / `AVAILABLE` / `COMPLETED` state, lesson counts and crowns |
| Lessons | `POST /api/lessons/{lesson_id}/start` | Start an attempt |
| | `POST /api/attempts/{attempt_id}/answer` | Submit one answer |
| | `POST /api/attempts/{attempt_id}/complete` | Finish a fully solved attempt |
| | `POST /api/attempts/{attempt_id}/abandon` | Abandon an active attempt |
| | `POST /api/skills/{skill_id}/claim-treasure` | Claim a treasure chest (30 gems, 0 XP) |
| Hearts | `GET /api/hearts` | Current hearts, next-heart timer, refill cost, gems |
| | `POST /api/hearts/refill` | Body `{"method": "GEMS" \| "PRACTICE"}` |
| Leaderboard | `GET /api/leaderboard` | Weekly XP ranking of the learner and seeded rivals |
| Dev | `GET /api/dev/clock` | Read the simulated clock |
| | `POST /api/dev/clock/advance` | Body `{"days": n}` (n ≥ 1) |
| | `POST /api/dev/clock/reset` | Reset the offset to 0 |
| System | `GET /api/health` | `{"status": "ok"}` |

The dev routes are registered only when `ENABLE_DEV_ENDPOINTS=true` (the default).

**Answer payload.** `AnswerRequest` takes `exercise_id` plus the field that fits the exercise type. Extra fields are rejected.

| Exercise type | Send |
| --- | --- |
| Multiple choice, fill in the blank (with options) | `option_id` |
| Translate (word bank) | `option_ids`, the tiles in order |
| Match pairs | `left_option_id` and `right_option_id` (one pair per call) |
| Type answer, fill in the blank (typed) | `text` |

Typed answers are compared after lower-casing and stripping punctuation and extra whitespace, against every row in `exercise_accepted_answers`.

## `/compat` reference (frontend adapter)

All routes are under `/compat/api`.

| Method and path | Description | Delegates to |
| --- | --- | --- |
| `GET /user/me` | Learner stats in the UI's shape (`xp_total`, `streak_count`, `hearts`, `gems`, leaderboard unlock flag, reward values) | stats services |
| `GET /course/path` | Units → skills with `status`, `kind` (`lesson`, `chest`, `practice`), `progress` and `is_legendary` | `build_path` |
| `POST /course/units/{unit_id}/jump` | "Jump here?" affordance. **A safe no-op**: it returns the unchanged path | none |
| `POST /course/chest/{skill_id}/open` | Open a treasure chest. Returns `{claimed, unlocked_skill_title}`; an already-claimed chest returns `claimed: false` | `claim_treasure` |
| `GET /course/units/{unit_id}/guidebook` | Up to 8 key phrases derived from the unit's own exercises | exercises and answers |
| `GET /lesson/{skill_id}/start` | Start the next unfinished lesson in a skill; returns the attempt id and exercises with answers | `lessons.start` |
| `POST /lesson/{attempt_id}/mistake` | Persist one wrong answer; returns `{hearts, max_hearts}` | writes `attempt_answers` + `heart_events` |
| `POST /lesson/{attempt_id}/complete` | Complete with `{correct_count, mistake_count}`; returns XP, hearts, streak, accuracy, unlocked skill | `lessons.complete` |
| `GET /lesson/{skill_id}/legendary` | Start a Legendary replay (requires every lesson in the skill to be completed, else `423`) | `lessons.start` |
| `POST /lesson/{skill_id}/legendary/complete` | Complete Legendary; 40 XP, and earns the badge if mistakes ≤ 3 | `lessons.complete` |
| `POST /hearts/refill` | Refill with gems, falling back to the practice refill if gems are short. At full hearts it returns the current state | `hearts.refill` |
| `GET /leaderboard` | Weekly ranking; `423 LEADERBOARD_LOCKED` until 2 lessons are completed | `get_leaderboard` |
| `POST /exercise/explain` | Placeholder explanation text for the "Explain" button | none |

**Exercise shapes returned by `/compat`**

| `type` | `payload` |
| --- | --- |
| `multiple_choice` | `{question, options[], correct}` |
| `translate` | `{prompt, word_bank[], correct_sequence[]}` |
| `match_pairs` | `{pairs: [{left, right}]}` |
| `fill_blank` | `{sentence, options[], correct}` (empty `options` means typed) |
| `type_answer` | `{prompt, correct}` |

**Where compat state lives without new tables**

- Legendary badges are remembered in the existing `system_settings` table under keys like `compat:legendary:{user_id}:{skill_id}`.
- Treasure claims are recorded as the native zero-XP `COMPLETED` attempt.
- The seeded practice nodes have no exercises, so they appear on the path but aren't playable yet.

## Business rules

Constants live in `app/constants.py`; a few UI rewards (Legendary, practice) are defined in `services/compat.py`.

| Rule | Value |
| --- | --- |
| Maximum hearts | 5 |
| Heart regeneration | 1 heart per 30 minutes while below the maximum |
| Wrong answer | −1 heart (a `LOST` event) |
| Gem refill | 100 gems fills all missing hearts |
| Practice refill | +1 heart |
| Treasure chest | +30 gems, 0 XP |
| Lesson XP | 10 per completed lesson (`lessons.xp_reward`) |
| Legendary XP | 40; badge if ≤ 3 mistakes |
| Practice XP (UI) | 5 |
| Timed practice limit | 180 seconds |
| Default daily goal | 20 XP (allowed: 10, 20, 30, 50) |
| Leaderboard unlock | 2 completed lessons |

**Derived values.** These are computed from events, never stored:

- **XP** is the sum of `xp_earned` over completed, non-treasure attempts.
- **Streak** is the count of consecutive days with a completed non-treasure lesson.
- **Hearts** come from replaying the `heart_events` ledger plus time regeneration.
- **Crowns** equal the number of completed lessons in a skill.
- **Skill state** (locked, available, completed) comes from order and completion.
- **Weekly leaderboard** is XP summed per user for the current Monday-to-Sunday week.

## Simulated clock

All timestamps are naive UTC. `app.clock.now_utc()` returns real UTC time plus `system_settings.time_offset_days`. Streaks, daily XP, weekly leaderboard periods and heart regeneration all use this clock.

To test day-dependent behaviour without waiting, advance the clock:

```bash
curl -X POST localhost:8000/api/dev/clock/advance \
     -H 'Content-Type: application/json' -d '{"days": 1}'
curl -X POST localhost:8000/api/dev/clock/reset
```

Advancing the clock does not change stored history. It changes which day "today" is.

## Database

SQLite, 15 tables, with foreign keys enforced on every connection (`PRAGMA foreign_keys=ON`). Tables are created at startup with `Base.metadata.create_all`. There are no migrations.

| Group | Tables |
| --- | --- |
| Content | `courses`, `units`, `skills`, `lessons`, `exercises`, `exercise_options`, `exercise_accepted_answers` |
| Learner state | `users`, `user_settings`, `lesson_attempts`, `attempt_answers`, `heart_events` |
| Gamification and system | `achievements`, `user_achievements`, `system_settings` |

Constraints, indexes, delete behaviour, enums and the reasoning behind the derived-versus-stored split are documented in [`SCHEMA_DESIGN_FINAL.md`](SCHEMA_DESIGN_FINAL.md).

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///<backend>/duolingo.db` | SQLAlchemy database URL |
| `AUTO_SEED` | `false` | Run the seed on startup |
| `ENABLE_DEV_ENDPOINTS` | `true` | Register `/api/dev/*` (set `false` in production) |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated allowed browser origins. Set this to your deployed frontend URL |

Static files are served from `/static` (`static/audio/` is reserved for exercise audio).

## Tests

```bash
pytest
```

The suite lives in `tests/` (`test_core.py` for the native API, `test_compat.py` for the adapter). It uses an isolated in-memory SQLite database with foreign keys enforced, so it never touches `duolingo.db`.
