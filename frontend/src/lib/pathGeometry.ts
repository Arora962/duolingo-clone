const LOBE = [0, 44.9, 70, 44.9, 0, 0] as const;

export function nodeLayout(
  index: number,
  unitIndex: number,
  hasStart: boolean,
  isLast: boolean,
) {
  const sign = unitIndex % 2 === 0 ? 1 : -1;
  const dx = LOBE[index % LOBE.length] * sign;
  const previous = index === 0 ? 0 : LOBE[(index - 1) % LOBE.length] * sign;
  const step = Math.abs(dx - previous);
  const marginTop =
    index === 0
      ? 24 + (hasStart ? 43 : 0)
      : Math.sqrt(89 ** 2 - step ** 2) - 65;

  return {
    dx,
    marginTop,
    marginBottom: isLast ? 24 : 0,
  };
}
