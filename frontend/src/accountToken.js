// Token sesji konta. Leży w localStorage tej przeglądarki (albo okna aplikacji)
// i idzie do serwera przy każdym połączeniu (socket.js), więc po odświeżeniu
// czy zerwanym połączeniu gracz jest od razu zalogowany.
const TOKEN_KEY = 'orlog.account'

export function loadToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch (e) {
    return ''
  }
}

export function saveToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch (e) {
    // bez localStorage trzeba się logować po każdym odświeżeniu
  }
}
