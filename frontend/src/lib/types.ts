// Types mirror the FastAPI response models in backend/app/schemas/.

export type CourseSummary = {
  id: number;
  language_code: string;
  name: string;
  flag_emoji: string;
};

export type Me = {
  id: number;
  username: string;
  display_name: string;
  avatar_url: string | null;
  gems: number;
  total_xp: number;
  current_streak: number;
  streak_active_today: boolean;
  hearts: number;
  max_hearts: number;
  next_heart_in_seconds: number | null;
  daily_goal_xp: number;
  xp_today: number;
  daily_goal_met: boolean;
  current_course: CourseSummary | null;
};

// ---------- Path ----------
export type NodeState = "LOCKED" | "AVAILABLE" | "COMPLETED";
export type SkillType = "LESSON" | "TREASURE" | "PRACTICE";

export type LessonNode = {
  id: number;
  position: number;
  xp_reward: number;
  state: NodeState;
};

export type SkillNode = {
  id: number;
  position: number;
  title: string;
  skill_type: SkillType;
  icon_type: string;
  state: NodeState;
  is_current: boolean;
  lessons_total: number;
  lessons_completed: number;
  progress_ratio: number;
  crowns: number;
  crowns_max: number;
  next_lesson_id: number | null;
  lessons: LessonNode[];
};

export type UnitNode = {
  id: number;
  position: number;
  title: string;
  description: string;
  color_bg: string;
  color_border: string;
  skills_completed: number;
  skills_total: number;
  skills: SkillNode[];
};

export type PathResponse = { course: CourseSummary; units: UnitNode[] };

// ---------- Lessons ----------
export type ExerciseOption = {
  id: number;
  text: string;
  image_emoji: string | null;
};

type ExerciseBase = {
  id: number;
  position: number;
  prompt: string;
  source_text: string | null;
  hint: string | null;
  audio_url: string | null;
};

export type MultipleChoiceExercise = ExerciseBase & {
  type: "MULTIPLE_CHOICE";
  options: ExerciseOption[];
};
// Fill-in-the-blank is either option-based or free typing.
export type FillInBlankExercise = ExerciseBase & {
  type: "FILL_IN_BLANK";
  options?: ExerciseOption[];
  requires_typing?: true;
};
export type TranslateWordBankExercise = ExerciseBase & {
  type: "TRANSLATE_WORD_BANK";
  tiles: { id: number; text: string }[];
};
export type MatchPairsExercise = ExerciseBase & {
  type: "MATCH_PAIRS";
  left: { id: number; text: string }[];
  right: { id: number; text: string }[];
};
export type TypeAnswerExercise = ExerciseBase & { type: "TYPE_ANSWER" };

export type Exercise =
  | MultipleChoiceExercise
  | FillInBlankExercise
  | TranslateWordBankExercise
  | MatchPairsExercise
  | TypeAnswerExercise;

export type StartLessonResponse = {
  attempt_id: number;
  lesson_id: number;
  skill: { id: number; title: string; skill_type: SkillType };
  mode: "STANDARD" | "TIMED_PRACTICE";
  xp_reward: number;
  hearts: number;
  max_hearts: number;
  time_limit_seconds: number | null;
  expires_at: string | null;
  total_exercises: number;
  exercises: Exercise[];
};

// Send only the fields your exercise type needs.
export type AnswerPayload =
  | { exercise_id: number; option_id: number } // multiple choice / fill blank
  | { exercise_id: number; option_ids: number[] } // word bank (ordered)
  | { exercise_id: number; text: string } // type answer / typed blank
  | { exercise_id: number; left_option_id: number; right_option_id: number }; // one pair

export type AnswerResult = {
  is_correct: boolean;
  correct_answer: string | null;
  speak_text: string | null;
  speak_lang: string | null;
  audio_url: string | null;
  exercise_solved: boolean;
  solved_exercises: number;
  total_exercises: number;
  progress_percent: number;
  all_exercises_solved: boolean;
  hearts: number;
  next_heart_in_seconds: number | null;
  lesson_failed: boolean;
  failure_reason: string | null;
};

export type CompleteResult = {
  xp_earned: number;
  total_xp: number;
  accuracy_percent: number;
  time_spent_seconds: number;
  streak_before: number;
  streak_after: number;
  streak_extended: boolean;
  xp_today: number;
  daily_goal_xp: number;
  goal_just_met: boolean;
  hearts: number;
  skill: {
    id: number;
    state: NodeState;
    lessons_completed: number;
    lessons_total: number;
    crowns: number;
  };
  skill_just_completed: boolean;
  next_skill_unlocked: { id: number; title: string } | null;
  newly_unlocked_achievements: {
    code: string;
    name: string;
    description: string;
    icon: string;
  }[];
};

export type TreasureResponse = { gems_awarded: number; gems: number };

// ---------- Hearts ----------
export type HeartsResponse = {
  hearts: number;
  max_hearts: number;
  next_heart_in_seconds: number | null;
  refill_cost_gems: number;
  gems: number;
};
export type RefillMethod = "GEMS" | "PRACTICE";
export type RefillResponse = HeartsResponse & { method: RefillMethod };

// ---------- Leaderboard / Profile / Settings ----------
export type LeaderboardEntry = {
  rank: number;
  user_id: number;
  username: string;
  display_name: string;
  avatar_url: string | null;
  weekly_xp: number;
  is_current_user: boolean;
  is_bot: boolean;
};
export type LeaderboardResponse = {
  period_start: string;
  period_end: string;
  days_remaining: number;
  current_user_rank: number | null;
  entries: LeaderboardEntry[];
};

export type AchievementProgress = {
  code: string;
  name: string;
  description: string;
  icon: string;
  metric: string;
  threshold: number;
  current_value: number;
  earned: boolean;
  unlocked_at: string | null;
};
export type ProfileResponse = {
  user: {
    id: number;
    username: string;
    display_name: string;
    avatar_url: string | null;
    joined_at: string;
  };
  stats: {
    total_xp: number;
    current_streak: number;
    longest_streak: number;
    lessons_completed: number;
    perfect_lessons: number;
    xp_today: number;
    daily_goal_xp: number;
    gems: number;
  };
  course: CourseSummary | null;
  achievements: AchievementProgress[];
};

export type Settings = {
  daily_goal_xp: 10 | 20 | 30 | 50;
  sound_effects_enabled: boolean;
  dark_mode_enabled: boolean;
  reminders_enabled: boolean;
};

export type Clock = {
  time_offset_days: number;
  simulated_now: string;
  simulated_today: string;
};