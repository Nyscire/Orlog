// Most między oknem gry a Electronem. Strona dostaje informację, że działa w aplikacji,
// numer wersji, okno kolejnego gracza i stan aktualizacji; żadnego dostępu do Node.
const { contextBridge, ipcRenderer } = require('electron')

const info = ipcRenderer.sendSync('orlog:info') || {}

// nowe okno gracza startuje z ustawieniami (motyw, język, serwer) okna, z którego je otwarto
if (info.seed) {
  for (const [key, value] of Object.entries(info.seed)) {
    try {
      if (value !== null && localStorage.getItem(key) === null) localStorage.setItem(key, value)
    } catch (e) {
      // bez localStorage okno użyje ustawień domyślnych
    }
  }
}

contextBridge.exposeInMainWorld('orlog', {
  app: true,
  version: info.version || '',
  platform: info.platform || '',
  packaged: !!info.packaged,
  player: info.player || 1,
  newWindow: () => ipcRenderer.send('orlog:new-window'),
  // aktualizacje: stan ({ status, version, percent, manual, needsPassword }) i akcje
  updateState: () => ipcRenderer.invoke('orlog:update-state'),
  onUpdate: callback => {
    ipcRenderer.on('orlog:update', (event, state) => callback(state))
  },
  installUpdate: () => ipcRenderer.send('orlog:update-install'),
  openDownloadPage: () => ipcRenderer.send('orlog:update-download-page')
})
