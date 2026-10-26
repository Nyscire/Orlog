// Adres serwera gry.
//
// Kolejność: adres wpisany w ustawieniach > adres wbudowany przy budowaniu (VITE_BACKEND_URL)
// > ten sam host co strona, port 5000 (gdy gra działa w przeglądarce, np. npm run dev).
// W aplikacji (Electron) strona nie ma „swojego” hosta, więc bez dwóch pierwszych adresu nie ma.
const STORAGE_KEY = 'orlog.server'
const DEFAULT_PORT = 5000

export const isApp = typeof window !== 'undefined' && !!(window.orlog && window.orlog.app)
export const appVersion = (isApp && window.orlog.version) || ''

function pageServer() {
  if (typeof window === 'undefined') return ''
  const { protocol, hostname } = window.location
  if (protocol !== 'http:' && protocol !== 'https:') return ''
  return `${protocol}//${hostname}:${DEFAULT_PORT}`
}

export function builtInServer() {
  return normalizeServer(import.meta.env.VITE_BACKEND_URL || '') || ''
}

export function defaultServer() {
  return builtInServer() || pageServer()
}

export function savedServer() {
  try {
    return localStorage.getItem(STORAGE_KEY) || ''
  } catch (e) {
    return ''
  }
}

export function serverUrl() {
  return savedServer() || defaultServer()
}

// "1.2.3.4" -> "http://1.2.3.4:5000", "gra.example.com:8000" -> "http://gra.example.com:8000",
// "https://gra.example.com" zostaje bez zmian. Zwraca null dla czegoś, co nie jest adresem.
export function normalizeServer(input) {
  const text = String(input || '').trim()
  if (!text) return ''
  const hasScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(text)
  let url
  try {
    url = new URL(hasScheme ? text : `http://${text}`)
  } catch (e) {
    return null
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return null
  if (!url.hostname || url.username || url.password) return null
  if (!hasScheme && !url.port) url.port = String(DEFAULT_PORT)
  // sam adres serwera, bez ścieżki i parametrów
  return url.origin
}

// Zapisuje adres (pusty = wróć do domyślnego). Zwraca false dla niepoprawnego adresu.
export function saveServer(input) {
  const url = normalizeServer(input)
  if (url === null) return false
  try {
    if (url && url !== defaultServer()) localStorage.setItem(STORAGE_KEY, url)
    else localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    return false
  }
  return true
}
