// Ustawienia wyglądu i języka, zapamiętywane w tej przeglądarce
import { reactive } from 'vue'

const STORAGE_KEY = 'orlog.settings'

export const LANGUAGES = [
  { id: 'pl', label: 'Polski' },
  { id: 'en', label: 'English' }
]
export const THEMES = ['classic', 'frost', 'ember', 'forest', 'night', 'abyss']
export const FONTS = ['classic', 'medieval', 'readable']
export const SIZES = ['normal', 'large']

const OPTIONS = {
  locale: LANGUAGES.map(l => l.id),
  theme: THEMES,
  font: FONTS,
  size: SIZES
}

function browserLocale() {
  const lang = (typeof navigator !== 'undefined' && navigator.language) || 'pl'
  return lang.toLowerCase().startsWith('pl') ? 'pl' : 'en'
}

function load() {
  const values = { locale: browserLocale(), theme: 'classic', font: 'classic', size: 'normal' }
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
    if (saved && typeof saved === 'object') {
      for (const key of Object.keys(OPTIONS)) {
        if (OPTIONS[key].includes(saved[key])) values[key] = saved[key]
      }
    }
  } catch (e) {
    // bez localStorage zostają wartości domyślne
  }
  return values
}

export const settings = reactive(load())

// motyw, czcionka i wielkość tekstu działają przez atrybuty na <html> (zob. theme.css)
export function applySettings() {
  const root = document.documentElement
  root.lang = settings.locale
  root.dataset.theme = settings.theme
  root.dataset.font = settings.font
  root.dataset.size = settings.size
}

export function setSetting(key, value) {
  if (!OPTIONS[key] || !OPTIONS[key].includes(value)) return
  settings[key] = value
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...settings }))
  } catch (e) {
    // jak wyżej
  }
  applySettings()
}
