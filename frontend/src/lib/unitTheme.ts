export type UnitTheme = {
  background: string;
  border: string;
};

export function unitTheme(colorBg: string, colorBorder: string): UnitTheme {
  return {
    background: colorBg,
    border: colorBorder,
  };
}
