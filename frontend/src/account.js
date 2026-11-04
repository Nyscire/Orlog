// Konto gracza: logowanie, rejestracja, reset hasła oraz profil i ranking z serwera.
// Konto jest opcjonalne: gość gra pod wpisanym imieniem, ale tylko w partiach normalnych.
import { reactive } from 'vue'
import socket from './socket'
import { settings } from './settings'
import { saveToken } from './accountToken'

export const account = reactive({
  user: null,          // { id, login, email, rating }
  known: false,        // serwer już powiedział, czy to połączenie jest zalogowane
  expired: false,      // zapisana sesja wygasła (albo hasło zmieniono na innym urządzeniu)
  pending: '',         // 'login' | 'register' | 'reset' | 'code' | 'logout': czekamy na serwer
  error: null,         // { code, params, form } ostatniego błędu formularza
  resetSentTo: '',     // login albo e-mail, dla którego poszedł kod
  profile: null,       // ostatnio oglądany profil (albo { login, missing: true })
  ranking: null        // lista najlepszych graczy
})

socket.on('account', data => {
  account.known = true
  account.user = data.user || null
  // nowy token po zalogowaniu; brak konta oznacza, że stary token już nic nie znaczy
  if (data.token) saveToken(data.token)
  else if (!data.user) saveToken(null)
  if (data.expired !== undefined) account.expired = !!data.expired
  if (data.user) account.expired = false
  if (data.token || !data.user) {
    account.pending = ''
    account.error = null
  }
})

socket.on('account_error', error => {
  account.pending = ''
  account.error = error
})

socket.on('reset_sent', data => {
  account.pending = ''
  account.error = null
  account.resetSentTo = data.login || ''
})

socket.on('profile', profile => {
  account.profile = profile
})

// kolejna strona historii partii doklejana do oglądanego profilu
socket.on('history', history => {
  const profile = account.profile
  if (!profile || profile.login !== history.login) return
  profile.history = { matches: [...profile.history.matches, ...history.matches], more: history.more }
})

socket.on('ranking', data => {
  account.ranking = data.players || []
})

socket.on('disconnect', () => {
  account.pending = ''
})

function send(event, form, payload) {
  account.pending = form
  account.error = null
  socket.emit(event, payload)
}

export function register(login, email, password) {
  send('register', 'register', { login, email, password })
}

export function logIn(login, password) {
  send('login', 'login', { login, password })
}

export function logOut() {
  send('logout', 'logout')
}

export function requestReset(login) {
  account.resetSentTo = ''
  send('reset_request', 'reset', { login, lang: settings.locale })
}

export function confirmReset(login, code, password) {
  send('reset_confirm', 'code', { login, code, password })
}

export function clearAccountError() {
  account.error = null
}

export function loadProfile(login) {
  account.profile = null
  socket.emit('get_profile', { login: login || null })
}

export function loadMoreHistory() {
  const profile = account.profile
  const matches = profile?.history?.matches || []
  if (!profile || !matches.length) return
  socket.emit('get_history', { login: profile.login, before: matches[matches.length - 1].id })
}

export function loadRanking() {
  socket.emit('get_ranking')
}
