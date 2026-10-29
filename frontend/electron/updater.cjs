// Aktualizacje aplikacji z wydań na GitHubie (electron-updater).
//
// Zainstalowana aplikacja sprawdza przy starcie i co godzinę, czy jest nowsze wydanie:
//   - instalator na Windowsa i AppImage: nowa wersja pobiera się w tle, a po pobraniu gra
//     proponuje ponowne uruchomienie (albo instaluje ją przy zamknięciu),
//   - paczka .deb: pobiera się w tle, a instalacja pyta o hasło, więc tylko na żądanie gracza,
//   - przenośny .exe nie umie się podmienić: tylko informacja i link do strony z wydaniami.
// Aplikacja uruchomiona z kodu (npm run app) niczego nie sprawdza.
//
// ORLOG_UPDATE_URL=http://... podmienia źródło aktualizacji (katalog z latest*.yml), np. do testów.
const { app, shell } = require('electron')

const RELEASES_URL = 'https://github.com/Nyscire/Orlog/releases/latest'
const CHECK_EVERY = 60 * 60 * 1000

function setupUpdates({ onState, log = () => {} }) {
  const feedUrl = process.env.ORLOG_UPDATE_URL || ''
  if (!app.isPackaged) return null

  const { autoUpdater } = require('electron-updater')
  const portable = !!process.env.PORTABLE_EXECUTABLE_DIR
  const deb = autoUpdater.constructor.name === 'DebUpdater'

  autoUpdater.logger = null
  autoUpdater.autoDownload = !portable
  // instalacja .deb wymaga hasła, więc nie robimy jej po cichu przy zamknięciu
  autoUpdater.autoInstallOnAppQuit = !portable && !deb
  if (feedUrl) autoUpdater.setFeedURL({ provider: 'generic', url: feedUrl })

  let state = { status: 'idle', version: '', percent: 0, manual: portable, needsPassword: deb }
  const update = changes => {
    state = { ...state, ...changes }
    onState(state)
  }

  autoUpdater.on('update-available', info => {
    log(`dostępna wersja ${info.version}`)
    update({ status: portable ? 'available' : 'downloading', version: info.version, percent: 0 })
  })
  autoUpdater.on('download-progress', progress => {
    update({ status: 'downloading', percent: Math.round(progress.percent || 0) })
  })
  autoUpdater.on('update-downloaded', info => {
    log(`pobrano wersję ${info.version}`)
    update({ status: 'ready', version: info.version, percent: 100 })
  })
  autoUpdater.on('error', error => {
    // brak sieci albo wydania to nic pilnego: po prostu spróbujemy później
    log(`błąd aktualizacji: ${error && error.message}`)
    if (state.status === 'downloading') update({ status: 'error' })
  })

  const check = () => autoUpdater.checkForUpdates().catch(error => log(`sprawdzanie: ${error && error.message}`))

  return {
    start(delay = 5000) {
      setTimeout(check, delay)
      setInterval(check, CHECK_EVERY).unref?.()
    },
    check,
    getState: () => state,
    install() {
      if (state.status !== 'ready') return
      // bez okien instalatora (Windows) i z ponownym uruchomieniem gry po aktualizacji
      autoUpdater.quitAndInstall(true, true)
    },
    openDownloadPage() {
      shell.openExternal(RELEASES_URL)
    },
    onDownloaded(callback) {
      autoUpdater.on('update-downloaded', callback)
    },
    onError(callback) {
      autoUpdater.on('error', callback)
    }
  }
}

module.exports = { setupUpdates, RELEASES_URL }
