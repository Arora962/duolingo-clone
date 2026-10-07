type Props = {
  value: string;
  placeholder?: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function TypeAnswer({ value, placeholder = "Type your answer", disabled, onChange, onSubmit }: Props) {
  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="sr-only" htmlFor="lesson-answer">
        Your answer
      </label>
      <input
        id="lesson-answer"
        autoComplete="off"
        autoCapitalize="off"
        spellCheck={false}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-2xl border-2 border-swan bg-white px-5 py-4 text-xl font-extrabold text-eel outline-none transition placeholder:text-hare focus:border-macaw focus:ring-4 focus:ring-[#dff3ff] disabled:bg-polar"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="mt-4 w-full rounded-xl bg-macaw px-6 py-4 text-sm font-black uppercase tracking-wide text-white shadow-btn-blue transition active:translate-y-1 active:shadow-none disabled:cursor-not-allowed disabled:opacity-50"
      >
        Check
      </button>
    </form>
  );
}
