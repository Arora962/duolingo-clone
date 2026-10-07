import type { NextPage } from "next";
import { useRouter } from "next/router";
import { LessonPlayer } from "~/components/lesson/LessonPlayer";

const LessonPage: NextPage = () => {
  const router = useRouter();
  const raw = router.query.lessonId;
  const lessonId = Array.isArray(raw) ? Number(raw[0]) : Number(raw);

  if (!router.isReady || !Number.isInteger(lessonId) || lessonId <= 0) {
    return <main className="min-h-screen bg-white" />;
  }

  return <LessonPlayer lessonId={lessonId} />;
};

export default LessonPage;
