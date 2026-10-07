# Architecture Documentation

## Overview

This is a full-stack Duolingo clone featuring a gamified language learning experience. The application follows a client-server architecture with a React/Next.js frontend and a FastAPI backend, using SQLite for persistent storage.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Client)                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Next.js 15 (App Router) + React 19 + TypeScript         │   │
│  │  ├─ Pages: /learn, /lesson, /profile, /quests, etc.      │   │
│  │  ├─ Components: Lesson player, path visualization        │   │
│  │  ├─ Hooks: Custom state management                       │   │
│  │  └─ Lib: API client, utilities, types                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                         HTTP/JSON                               │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Server)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Routers (HTTP Layer)                                    │   │
│  │  ├─ /api/*        - Native API endpoints                 │   │
│  │  ├─ /compat/*     - UI adapter endpoints                 │   │
│  │  └─ /health       - Health check                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Services (Business Logic Layer)                         │   │
│  │  ├─ lessons.py    - Lesson lifecycle & exercise grading  │   │
│  │  ├─ path.py       - Skill tree & progression             │   │
│  │  ├─ hearts.py     - Heart system & regeneration          │   │
│  │  ├─ leaderboard.py- Weekly rankings                      │   │
│  │  ├─ achievements.py- Achievement tracking                │   │
│  │  ├─ stats.py      - Derived metrics (XP, streak, etc.)   │   │
│  │  └─ answers.py    - Answer validation & grading          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Models (Data Layer - SQLAlchemy ORM)                    │   │
│  │  ├─ content.py    - Course, Unit, Skill, Lesson, Exercise│   │
│  │  ├─ learner.py    - User, UserSettings                   │   │
│  │  └─ gamification.py- LessonAttempt, HeartEvent, etc.     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                         SQLAlchemy ORM
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database                              │
│                                                                 │
│  Content Tables (Shared):                                       │
│  ├─ courses, units, skills, lessons                             │
│  ├─ exercises, exercise_options, exercise_accepted_answers      │
│                                                                 │
│  Learner State Tables (Per-user):                               │
│  ├─ users, user_settings                                        │
│  ├─ lesson_attempts, attempt_answers                            │
│  ├─ heart_events                                                │
│                                                                 │
│  Gamification Tables:                                           │
│  ├─ achievements, user_achievements                             │
│  ├─ system_settings                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

### 1. **Server-Driven Game State**
- The server owns all game logic and state (XP, hearts, streak, unlocks)
- The browser only renders UI and sends user actions
- This prevents cheating and ensures consistency

### 2. **Derived Metrics**
- XP, streak, hearts, and crowns are **computed on-demand**, not stored
- They're derived from `lesson_attempts` and `heart_events`
- This prevents data drift and simplifies updates

### 3. **Immutable History**
- `lesson_attempts` and `attempt_answers` are append-only
- Once recorded, they cannot be modified or deleted
- This creates an audit trail and enables replay

### 4. **Two API Surfaces**
- **`/api`**: Native API - hides answers, grades server-side
- **`/compat`**: UI adapter - returns shapes the frontend needs, allows local checking

### 5. **Relational Exercises**
- Exercise options and accepted answers are database rows, not JSON
- This keeps them queryable and enforces constraints
- Enables complex exercise types (match pairs, fill-in-blank)

## Data Flow

### Lesson Attempt Flow

```
1. User clicks "Start Lesson"
   └─> GET /compat/lessons/{lesson_id}/start
       └─> Service: Create LessonAttempt (IN_PROGRESS)
           └─> Return exercises with options/tiles

2. User submits answer
   └─> POST /compat/lessons/{lesson_id}/answer
       └─> Service: Check answer, record AttemptAnswer
           └─> Return feedback (correct/incorrect)

3. User completes lesson
   └─> POST /compat/lessons/{lesson_id}/complete
       └─> Service: Mark LessonAttempt (COMPLETED)
           └─> Calculate XP, update streak, check achievements
           └─> Return lesson complete modal data

4. Learner profile updates
   └─> Derived from lesson_attempts + heart_events
       └─> Total XP, current streak, hearts, crowns
```

### Heart Regeneration Flow

```
1. User loses a heart (wrong answer)
   └─> Service: Create HeartEvent (LOST)
       └─> Decrement current_hearts

2. Time passes (simulated or real)
   └─> GET /api/hearts/status
       └─> Service: Calculate current_hearts from HeartEvent history
           └─> If enough time passed, hearts regenerate

3. User refills hearts with gems
   └─> POST /api/hearts/refill
       └─> Service: Deduct gems, create HeartEvent (REFILLED)
           └─> Reset current_hearts to MAX
```

## Module Organization

### Backend (`backend/app/`)

```
app/
├── main.py              # FastAPI app setup, middleware, lifespan
├── config.py            # Environment configuration
├── database.py          # SQLAlchemy engine & session
├── constants.py         # Game constants (MAX_HEARTS, XP values, etc.)
├── enums.py             # Enumerations (ExerciseType, SkillType, etc.)
├── errors.py            # Custom exception classes
├── clock.py             # Simulated time for testing
├── deps.py              # Dependency injection (get_current_user, get_db)
│
├── models/              # SQLAlchemy ORM models
│   ├── content.py       # Course, Unit, Skill, Lesson, Exercise
│   ├── learner.py       # User, UserSettings
│   ├── gamification.py  # LessonAttempt, HeartEvent, Achievement
│   └── mixins.py        # TimestampMixin
│
├── routers/             # HTTP endpoint handlers
│   ├── compat.py        # UI adapter endpoints (/compat/*)
│   ├── lessons.py       # Lesson endpoints (/api/lessons/*)
│   ├── path.py          # Path endpoints (/api/path/*)
│   ├── hearts.py        # Heart endpoints (/api/hearts/*)
│   ├── leaderboard.py   # Leaderboard endpoints (/api/leaderboard/*)
│   ├── me.py            # User profile endpoints (/api/me/*)
│   └── dev.py           # Development endpoints (seeding, time control)
│
├── services/            # Business logic
│   ├── lessons.py       # Lesson lifecycle, exercise grading
│   ├── path.py          # Skill tree, progression logic
│   ├── hearts.py        # Heart system, regeneration
│   ├── leaderboard.py   # Ranking calculations
│   ├── achievements.py  # Achievement evaluation
│   ├── stats.py         # Derived metrics (XP, streak, etc.)
│   ├── answers.py       # Answer validation
│   └── compat.py        # UI adapter logic
│
├── schemas/             # Pydantic request/response models
│   ├── lessons.py       # Lesson DTOs
│   ├── path.py          # Path DTOs
│   ├── hearts.py        # Heart DTOs
│   ├── leaderboard.py   # Leaderboard DTOs
│   ├── me.py            # User profile DTOs
│   └── ...
│
├── seed.py              # Database seeding
├── seed_data.py         # Seeded content (Spanish course)
└── tests/               # Test suite
    ├── conftest.py      # Pytest fixtures
    ├── test_core.py     # Core functionality tests
    └── test_compat.py   # Compatibility layer tests
```

### Frontend (`frontend/src/`)

```
src/
├── app/                 # Next.js App Router pages
│   ├── layout.tsx       # Root layout with providers
│   ├── page.tsx         # Home page (redirects to /learn)
│   ├── learn/           # Learning path page
│   ├── lesson/          # Lesson player page
│   ├── profile/         # User profile page
│   ├── quests/          # Daily quests page
│   ├── leaderboard/     # Weekly leaderboard page
│   ├── shop/            # Shop page
│   ├── settings/        # Settings page
│   └── guidebook/       # Unit guidebook page
│
├── components/          # React components
│   ├── shared/          # Shared components
│   │   ├── AppChrome.tsx    # Main layout wrapper
│   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   ├── TopBar.tsx       # Top navigation bar
│   │   ├── ThemeProvider.tsx# Dark/light theme
│   │   ├── UserProvider.tsx # User context
│   │   └── ...
│   │
│   ├── lesson/          # Lesson player components
│   │   ├── ExerciseMultipleChoice.tsx
│   │   ├── ExerciseTranslate.tsx
│   │   ├── ExerciseMatchPairs.tsx
│   │   ├── ExerciseFillBlank.tsx
│   │   ├── ExerciseTypeAnswer.tsx
│   │   ├── FeedbackBar.tsx
│   │   ├── ProgressBar.tsx
│   │   └── ...
│   │
│   ├── path/            # Learning path components
│   │   ├── SkillNode.tsx    # Individual skill node
│   │   ├── UnitBanner.tsx   # Unit header
│   │   ├── ChestReward.tsx  # Treasure chest animation
│   │   └── ...
│   │
│   ├── rail/            # Right sidebar components
│   │   ├── RightRail.tsx    # Main rail container
│   │   ├── StatsRow.tsx     # XP, streak, hearts display
│   │   ├── DailyQuestsCard.tsx
│   │   └── ...
│   │
│   └── ...
│
├── hooks/               # Custom React hooks
│   ├── useActiveUnit.ts     # Track active unit in path
│   ├── useInView.ts         # Intersection observer hook
│   └── characterMotion.ts   # Animation hooks
│
├── lib/                 # Utility functions & types
│   ├── api.ts           # API client (fetch wrappers)
│   ├── types.ts         # TypeScript type definitions
│   ├── format.ts        # Formatting utilities
│   ├── status.ts        # Status calculations
│   ├── answers.ts       # Answer validation
│   ├── characters.ts    # Character data
│   ├── quests.ts        # Quest logic
│   ├── rail.ts          # Rail utilities
│   ├── speech.ts        # Text-to-speech
│   ├── pathGeometry.ts  # Path layout calculations
│   └── ...
│
├── globals.css          # Global styles
├── tailwind.config.ts   # Tailwind configuration
└── next-env.d.ts        # Next.js type definitions
```

## Database Schema

### Content Tables (Shared across learners)

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `courses` | Language courses | id, language_code, name, flag_emoji |
| `units` | Course units | id, course_id, position, title, color_bg |
| `skills` | Skills within units | id, unit_id, position, title, skill_type, icon_type |
| `lessons` | Lessons within skills | id, skill_id, position, xp_reward |
| `exercises` | Exercises within lessons | id, lesson_id, type, prompt, source_text |
| `exercise_options` | Options for exercises | id, exercise_id, text, is_correct, image_emoji |
| `exercise_accepted_answers` | Valid answers for typed exercises | id, exercise_id, text |

### Learner State Tables (Per-user)

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `users` | Learner accounts | id, username, display_name, gems, is_seeded_bot |
| `user_settings` | User preferences | user_id, daily_goal_xp, sound_effects_enabled, dark_mode_enabled |
| `lesson_attempts` | Lesson runs | id, user_id, lesson_id, status, started_at, finished_at, xp_earned |
| `attempt_answers` | Submitted answers | id, attempt_id, exercise_id, is_correct, submitted_text |
| `heart_events` | Heart history | id, user_id, event_type, created_at |

### Gamification Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `achievements` | Achievement definitions | id, code, name, description, metric, threshold |
| `user_achievements` | Earned achievements | id, user_id, achievement_id, earned_at |
| `system_settings` | Global settings | key, value |

## Key Algorithms

### XP Calculation
```python
total_xp = SUM(lesson_attempts.xp_earned WHERE status = 'COMPLETED')
xp_today = SUM(lesson_attempts.xp_earned WHERE status = 'COMPLETED' AND finished_at >= today_start)
```

### Streak Calculation
```python
# Streak is the number of consecutive days with XP >= daily_goal
# Resets if a day is missed
streak = COUNT(days_with_xp >= daily_goal) from most recent backwards
```

### Heart Regeneration
```python
# Hearts regenerate 1 per 24 hours (configurable)
# Max hearts = 5
current_hearts = MAX_HEARTS - COUNT(HeartEvent.LOST) + COUNT(HeartEvent.REGENERATED)
```

### Leaderboard Ranking
```python
# Weekly ranking based on XP earned in the current week
# Includes seeded bots with fixed XP values
ranking = ORDER BY xp_this_week DESC, user_id ASC
```

## API Contracts

### Native API (`/api/*`)

- **Hides answers** - Exercise options don't include correctness
- **Server-grades** - Answer checking happens on the backend
- **Structured errors** - Returns `{ detail: { code, message } }`

### Compatibility API (`/compat/*`)

- **Returns answers** - Exercise options include correctness for local checking
- **Client-grades** - Frontend validates answers before sending
- **UI-shaped responses** - Returns exactly what the Duolingo-style UI needs

## Testing Strategy

### Unit Tests
- Service functions with mocked database
- Answer validation logic
- Streak and XP calculations

### Integration Tests
- Full lesson flow (start → answer → complete)
- Heart regeneration over time
- Achievement unlocking

### Test Database
- Seeded with Spanish course (2 units, 8 skills, 40 exercises)
- Default learner with 110 XP, 3-day streak, 4 hearts
- 10 seeded bots for leaderboard testing

## Performance Considerations

### Indexes
- `lesson_attempts(user_id, status, finished_at)` - Fast streak/XP queries
- `lesson_attempts(lesson_id)` - Fast lesson completion checks
- `attempt_answers(attempt_id)` - Fast answer lookups

### Caching
- Derived metrics (XP, streak, hearts) are computed on-demand
- No caching layer needed due to small dataset size
- Could add Redis for production scaling

### Query Optimization
- Use `selectinload()` to eager-load relationships
- Avoid N+1 queries in lesson completion flow
- Batch heart event creation

## Security Considerations

### Authentication
- Simplified: Single seeded learner always signed in
- Production: Would use JWT or OAuth

### Authorization
- Users can only access their own data
- Enforced in `get_current_user` dependency

### Input Validation
- Pydantic models validate all request bodies
- Exercise IDs and lesson IDs are validated against user's course

### Answer Validation
- Server always re-validates answers
- Frontend validation is for UX only, not security

## Deployment

### Environment Variables
- `DATABASE_URL` - SQLite database path
- `CORS_ORIGINS` - Allowed frontend origins
- `AUTO_SEED` - Auto-seed database on startup
- `ENABLE_DEV_ENDPOINTS` - Enable development endpoints
- `SIMULATED_DAY_OFFSET` - For testing time-based features

### Database Migrations
- SQLAlchemy creates schema on startup
- No migration tool needed for this project
- Schema is defined in models and created via `Base.metadata.create_all()`

## Future Enhancements

1. **Multiple Languages** - Support more courses beyond Spanish
2. **Real Authentication** - JWT or OAuth integration
3. **Friends & Social** - Add friend system and social features
4. **Speech Recognition** - Implement actual speech input
5. **Real Payments** - Integrate payment processor for gems
6. **Mobile App** - React Native or Flutter version
7. **Analytics** - Track learning patterns and engagement
8. **Adaptive Learning** - Adjust difficulty based on performance
