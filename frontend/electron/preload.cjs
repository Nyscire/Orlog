// Most między oknem gry a Electronem. Strona dostaje tylko informację,
// że działa w aplikacji, i numer wersji; żadnego dostępu do Node.
const { contextBridge, ipcRenderer } = require('electron')

const info = ipcRenderer.sendSync('orlog:info') || {}

contextBridge.exposeInMainWorld('orlog', {
  app: true,
  version: info.version || '',
  platform: info.platform || ''
})
