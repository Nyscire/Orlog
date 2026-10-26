// Kolejność ścianek kości w legendzie i podsumowaniach (teksty są w locales/*.js)
export const FACE_ORDER = ['axe', 'arrow', 'helmet', 'shield', 'hand']

// ikona boga: public/img/gods/<imię małymi literami>.svg
export const godIcon = name => `/img/gods/${String(name || '').toLowerCase()}.svg`
