# Frontend

The Next.js (App Router) client for the Duolingo clone. It renders the learning path, the lesson player, and the profile, quests, shop and leaderboard pages. It talks to the backend over HTTP and holds no game rules of its own.

Back to the [project overview](../README.md). For the API it consumes, see the [backend README](../backend/README.md#compat-reference-frontend-adapter).

## Contents

- [Setup](#setup)
- [Configuration](#configuration)
- [Pages](#pages)
- [How the lesson player works](#how-the-lesson-player-works)
- [Project structure](#project-structure)
- [Data flow and API client](#data-flow-and-api-client)
- [Styling and design system](#styling-and-design-system)
- [Responsive layout](#responsive-layout)
- [Placeholders](#placeholders)

## Setup

Requires Node.js 18.18+ (20+ recommended). The backend must be running at http://localhost:8000. See the [backend setup](../backend/README.md#setup).

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

| Script | Purpose |
| --- | --- |
| `npm run dev` | Development server with hot reload |
| `npm run build` | Production build (type-checks and lints) |
| `npm start` | Serve the production build |
| `npm run lint` | ESLint (`next/core-web-vitals`, `next/typescript`) |

The Nunito font is loaded through `next/font/google`, so the first build needs internet access to fetch it.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/compat` | Base URL of the backend's **compat** API |

Create `frontend/.env.local` to override it:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.example.com/compat
```

Note two things:

- The value must **end in `/compat`**. The client's paths already start with `/api/...`, so requests resolve to `/compat/api/...`.
- It is a build-time `NEXT_PUBLIC_` variable, so rebuild after changing it.

When you deploy, also add the frontend's URL to the backend's `CORS_ORIGINS`.

## Pages

| Route | Page | Backend data |
| --- | --- | --- |
| `/` | Redirects to `/learn` | none |
| `/learn` | Learning path: units, skill nodes, progress rings, chests, unit characters and a sticky unit header | `course/path`, `course/chest/{id}/open`, `course/units/{id}/jump` |
| `/lesson/[skillId]` | Lesson player. Add `?mode=legendary` for the Legendary replay | `lesson/{id}/start`, `.../mistake`, `.../complete`, `.../legendary*` |
| `/guidebook/[unitId]` | Key phrases for a unit | `course/units/{id}/guidebook` |
| `/sections` | Course sections (the others are "coming soon") | `course/path` |
| `/leaderboard` | Weekly ranking with promotion zone | `leaderboard` |
| `/quests` | Daily quests derived from the learner's stats | `user/me` |
| `/shop` | Heart refill with gems | `hearts/refill` |
| `/profile` | Stats, streak, XP and current league | `user/me`, `leaderboard` |
| `/settings` | Settings placeholders | none |

All paths in the right-hand column are relative to `/compat/api`.

## How the lesson player works

`app/lesson/[skillId]/page.tsx` drives the loop:

1. **Start.** It fetches the lesson. The response includes the attempt id, the exercises and the current hearts.
2. **Answer.** Each exercise component checks the answer locally (`lib/answers.ts`) and calls one shared handler.
3. **Feedback.** The feedback bar slides up in green or red. A correct answer advances the progress bar. A wrong answer shows the correct solution.
4. **Hearts.** A wrong answer immediately calls `recordMistake`, so the heart is spent on the server and survives a refresh. At zero hearts the **Out of Hearts** modal blocks the lesson, with refill options.
5. **Finish.** After the last exercise it sends `{correct_count, mistake_count}`. The server awards XP, updates the streak and unlocks the next skill. The **Lesson Complete** modal shows the server's numbers.
6. **Refresh.** `UserProvider` refetches on every route change, so the top bar and right rail show the new XP, streak and hearts after returning to `/learn`.

Supported exercise types, one component each in `components/lesson/`:

| `type` | Component | Interaction |
| --- | --- | --- |
| `multiple_choice` | `ExerciseMultipleChoice` | Pick one option |
| `translate` | `ExerciseTranslate` | Tap words from the bank to build the sentence |
| `match_pairs` | `ExerciseMatchPairs` | Match left and right items; the right column is shuffled |
| `fill_blank` | `ExerciseFillBlank` | Choose or type the missing word |
| `type_answer` | `ExerciseTypeAnswer` | Type the answer. Matching ignores case, punctuation and accents |

Questions are read aloud with the browser's built-in **Web Speech API** (`lib/speech.ts`), so no audio files or API keys are needed. A speaker button replays the question, which also covers browsers that block autoplay speech.

## Project structure

```
src/
├── app/                    routes (App Router) and global styles
│   ├── layout.tsx          fonts, providers, app shell
│   ├── learn/ lesson/[skillId]/ guidebook/[unitId]/ sections/
│   ├── leaderboard/ quests/ shop/ profile/ settings/
│   └── globals.css         per-character animation keyframes and base styles
├── components/
│   ├── shared/             AppChrome, Sidebar, TopBar, DuoButton, providers, icons, assets
│   ├── layout/             RailLayout: content column plus right rail
│   ├── path/               SkillNode, UnitBanner, ChestReward, characters, popovers
│   ├── lesson/             exercise components, FeedbackBar, CheckFooter, modals, ProgressBar
│   ├── rail/               right-rail cards: stats, quests, Super promo, popovers
│   ├── sections/ leaderboard/ shop/ profile/ quests/ characters/
├── hooks/                  useActiveUnit, useInView, characterMotion
└── lib/
    ├── api.ts              typed fetch client (the only place that calls the backend)
    ├── types.ts            TypeScript mirror of the backend compat contract
    ├── answers.ts          answer normalisation and display helpers
    ├── pathGeometry.ts     winding-path layout maths
    ├── speech.ts           text-to-speech wrapper
    └── rail.ts, quests.ts, status.ts, format.ts, unitTheme.ts, characters.ts, exerciseText.ts
public/
├── duo/                    UI icons, nav icons, league and status art (SVG)
└── characters/             path mascot illustrations (SVG)
```

Responsibilities are separated as follows:

- **Pages** own data loading and screen-level state.
- **Components** are presentational and receive typed props.
- **`lib/`** holds pure logic and the API client.
- **Hooks** hold reusable behaviour (scroll tracking, animation).

## Data flow and API client

`lib/api.ts` is a thin `fetch` wrapper that builds URLs from `NEXT_PUBLIC_API_URL`, sends JSON, and disables caching (`cache: "no-store"`). Failures become an `ApiError` with a readable message:

- a network failure produces a "Can't reach the API… Is the backend running?" message;
- a structured backend error (`{detail: {code, message}}`) shows its `message`.

`lib/types.ts` mirrors the backend response shapes. If a backend schema changes, update this file.

Global state is deliberately small:

- `UserProvider` holds the learner's stats (`useUser()` gives `user`, `refresh`, `patch`).
- `ToastProvider` shows toasts and the "not available yet" notices (`useToast()`).

## Styling and design system

- **Tailwind CSS** with a custom `duo` palette in `tailwind.config.ts`: Duolingo green and blue, the dark background and card colours, border and text tones, and the right-rail tokens. The palette and spacing come from measurements of the reference UI.
- **Typeface:** Nunito, the closest free match to Duolingo's proprietary font.
- **Buttons:** the signature raised "3D" button with a pressed shadow (`DuoButton`).
- **Animation:** Framer Motion drives the path mascots (each with its own idle motion), and CSS keyframes (`slide-up`, `pop-in`, `float-pill`) drive the feedback bar, modals and pills. Motion respects `prefers-reduced-motion`.
- **Assets:** all icons and illustrations are local SVGs in `public/`, so the app works offline and doesn't depend on a third-party CDN.
- **Theme:** the UI is dark-themed, matching the reference.

## Responsive layout

`AppChrome` decides how much of the shell each page gets:

| Viewport | Layout |
| --- | --- |
| `xl` and up | Left sidebar, content column and right rail (stats, quests, promos) |
| `lg` to `xl` | Sidebar and content column; the stats strip moves to a top bar |
| Below `lg` | Content column with a top bar and a bottom tab bar |

The lesson player (`/lesson/*`) is intentionally chrome-free so nothing competes with the exercise.

## Placeholders

These are shown for visual fidelity but are not implemented. They show a "Coming soon" notice or do nothing:

- Sidebar items **Letters** and **Practice**
- **Settings** toggles (sound, dark mode, reminders)
- Sections 2 and 3
- Friends and follow panels, the Super subscription card, and "more daily quests"
- Speech recognition. Only text-to-speech is implemented.

The seeded practice nodes have no exercises yet, so they appear on the path but can't be played.
