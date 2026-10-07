type SpeakOptions = {
  enabled?: boolean;
  lang?: string;
  rate?: number;
  pitch?: number;
};

export function speechAvailable(): boolean {
  return (
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    "SpeechSynthesisUtterance" in window
  );
}

export function stopSpeaking(): void {
  if (!speechAvailable()) {
    return;
  }

  window.speechSynthesis.cancel();
}

export function speak(
  text: string,
  options: SpeakOptions = {},
): void {
  if (!options.enabled || !text.trim() || !speechAvailable()) {
    return;
  }

  stopSpeaking();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = options.lang ?? "en-US";
  utterance.rate = options.rate ?? 0.9;
  utterance.pitch = options.pitch ?? 1;

  window.speechSynthesis.speak(utterance);
}

export function playAudioOrSpeak(
  audioUrl: string | null,
  text: string | null,
  lang: string | null,
  enabled = true,
): void {
  if (!enabled) {
    return;
  }

  if (audioUrl && typeof window !== "undefined") {
    const audio = new Audio(audioUrl);

    void audio.play().catch(() => {
      if (text) {
        speak(text, {
          enabled: true,
          lang: lang ?? "en-US",
        });
      }
    });

    return;
  }

  if (text) {
    speak(text, {
      enabled: true,
      lang: lang ?? "en-US",
    });
  }
}