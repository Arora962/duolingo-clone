type SoundName = "correct" | "wrong" | "complete";

let audioContext: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  if (typeof window === "undefined") {
    return null;
  }

  const AudioContextConstructor =
    window.AudioContext ??
    (
      window as typeof window & {
        webkitAudioContext?: typeof AudioContext;
      }
    ).webkitAudioContext;

  if (!AudioContextConstructor) {
    return null;
  }

  audioContext ??= new AudioContextConstructor();

  if (audioContext.state === "suspended") {
    void audioContext.resume();
  }

  return audioContext;
}

function tone(
  context: AudioContext,
  frequency: number,
  start: number,
  duration: number,
  volume: number,
): void {
  const oscillator = context.createOscillator();
  const gain = context.createGain();

  oscillator.type = "sine";
  oscillator.frequency.setValueAtTime(frequency, start);

  gain.gain.setValueAtTime(0.0001, start);
  gain.gain.exponentialRampToValueAtTime(volume, start + 0.015);
  gain.gain.exponentialRampToValueAtTime(
    0.0001,
    start + Math.max(duration, 0.03),
  );

  oscillator.connect(gain);
  gain.connect(context.destination);

  oscillator.start(start);
  oscillator.stop(start + duration);
}

export function playSound(
  name: SoundName,
  enabled = true,
): void {
  if (!enabled) {
    return;
  }

  const context = getAudioContext();

  if (!context) {
    return;
  }

  const now = context.currentTime;

  if (name === "correct") {
    tone(context, 523.25, now, 0.12, 0.07);
    tone(context, 659.25, now + 0.09, 0.16, 0.06);
    return;
  }

  if (name === "wrong") {
    tone(context, 220, now, 0.14, 0.06);
    tone(context, 174.61, now + 0.08, 0.18, 0.05);
    return;
  }

  tone(context, 523.25, now, 0.14, 0.06);
  tone(context, 659.25, now + 0.1, 0.14, 0.06);
  tone(context, 783.99, now + 0.2, 0.22, 0.07);
}

export function playCorrectSound(enabled = true): void {
  playSound("correct", enabled);
}

export function playWrongSound(enabled = true): void {
  playSound("wrong", enabled);
}

export function playCompleteSound(enabled = true): void {
  playSound("complete", enabled);
}