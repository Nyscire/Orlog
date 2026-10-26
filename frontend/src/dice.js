// Kolejność ścianek kości w legendzie i podsumowaniach (teksty są w locales/*.js)
export const FACE_ORDER = ['axe', 'arrow', 'helmet', 'shield', 'hand']

// ikona boga: public/img/gods/<imię małymi literami>.svg
export const godIcon = name => `/img/gods/${String(name || '').toLowerCase()}.svg`

// Dymek kości jest wyśrodkowany nad kością i ma stałą szerokość (jak .tooltip-content w Die.vue).
export const TOOLTIP_WIDTH = 190

// O ile przesunąć dymek w poziomie, żeby nie wychodził poza okno (np. nad skrajną kością).
export function tooltipShift(rect, viewportWidth, width = TOOLTIP_WIDTH, margin = 8) {
  const left = rect.left + rect.width / 2 - width / 2
  const max = viewportWidth - margin - width
  // okno węższe niż dymek: przyklejony do lewej krawędzi
  if (max < margin) return margin - left
  return Math.min(Math.max(left, margin), max) - left
}
