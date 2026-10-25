// Tłumaczenia: $t('klucz', parametry) w komponentach.
// Wartością może być tekst z {parametrami} albo funkcja (np. dla polskiej odmiany).
import { settings } from './settings'
import { pl } from './locales/pl'
import { en } from './locales/en'

export const messages = { pl, en }

function lookup(tree, key) {
  return key.split('.').reduce((node, part) => (node == null ? undefined : node[part]), tree)
}

export function t(key, params = {}) {
  let value = lookup(messages[settings.locale], key)
  if (value === undefined) value = lookup(messages.pl, key)
  if (value === undefined) return key
  if (typeof value === 'function') return value(params)
  if (typeof value !== 'string') return value
  return value.replace(/\{(\w+)\}/g, (all, name) => (params[name] !== undefined ? params[name] : all))
}

// wpis z dziennika serwera: { type, params } -> zdanie w języku gracza
export function eventText(entry) {
  const text = t(`log.events.${entry.type}`, entry.params || {})
  return text === `log.events.${entry.type}` ? entry.type : text
}

// błąd z serwera: { code, params } -> komunikat w języku gracza
export function errorText(error) {
  if (!error) return ''
  if (typeof error === 'string') return error
  const text = t(`errors.${error.code}`, error.params || {})
  return text === `errors.${error.code}` ? t('errors.unknown', { code: error.code }) : text
}
