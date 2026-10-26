// Aplikacja Orlog w Electronie: okno z frontendem Vue, który łączy się z serwerem gry.
//
//   npm run app                       zbudowany frontend (dist/) w oknie aplikacji
//   npm run app:dev                   okno z serwerem deweloperskim Vite (npm run dev w drugim terminalu)
//   electron . --smoke-test[=plik]    test uruchomienia dla CI: sprawdza menu, robi zrzut ekranu i wychodzi
const { app, BrowserWindow, Menu, ipcMain, net, protocol, screen, shell } = require('electron')
const path = require('node:path')
const { pathToFileURL } = require('node:url')

// Pliki frontendu idą przez własny protokół app://orlog/..., a nie file://.
// Dzięki temu działają ścieżki od korzenia (/img/...), a localStorage ma stały adres.
const SCHEME = 'app'
const ORIGIN = `${SCHEME}://orlog`
const DIST = path.join(__dirname, '..', 'dist')

function argValue(name) {
  const prefix = `--${name}=`
  const arg = process.argv.find(a => a === `--${name}` || a.startsWith(prefix))
  if (arg === undefined) return undefined
  return arg.startsWith(prefix) ? arg.slice(prefix.length) : ''
}

const devUrl = argValue('dev-url') || null
const smokeShot = argValue('smoke-test')   // undefined: zwykłe uruchomienie
const allowDevTools = !app.isPackaged || argValue('devtools') !== undefined

protocol.registerSchemesAsPrivileged([
  { scheme: SCHEME, privileges: { standard: true, secure: true, supportFetchAPI: true } }
])

function serveDist() {
  protocol.handle(SCHEME, async request => {
    const { pathname } = new URL(request.url)
    const file = path.normalize(path.join(DIST, decodeURIComponent(pathname === '/' ? '/index.html' : pathname)))
    // nic spoza katalogu dist/
    if (file !== DIST && !file.startsWith(DIST + path.sep)) {
      return new Response('Not found', { status: 404 })
    }
    try {
      return await net.fetch(pathToFileURL(file).toString())
    } catch (e) {
      return new Response('Not found', { status: 404 })
    }
  })
}

// --- okno ---

let mainWindow = null

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  mainWindow = new BrowserWindow({
    width: Math.min(1440, width),
    height: Math.min(900, height),
    minWidth: 1024,
    minHeight: 640,
    title: 'Orlog',
    backgroundColor: '#2a1d14',
    icon: path.join(__dirname, '..', 'build', 'icon.png'),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
      spellcheck: false
    }
  })

  mainWindow.once('ready-to-show', () => {
    // na laptopach (np. 1366×768) od razu na cały ekran roboczy
    if (width <= 1440 || height <= 900) mainWindow.maximize()
    if (smokeShot === undefined) mainWindow.show()
  })

  const contents = mainWindow.webContents

  // linki zewnętrzne otwiera przeglądarka, a okno gry zostaje na swojej stronie
  contents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//.test(url)) shell.openExternal(url)
    return { action: 'deny' }
  })
  contents.on('will-navigate', (event, url) => {
    const allowed = devUrl ? new URL(devUrl).origin : ORIGIN
    if (new URL(url).origin !== allowed) {
      event.preventDefault()
      if (/^https?:\/\//.test(url)) shell.openExternal(url)
    }
  })

  // aplikacja nie ma paska menu, więc skróty obsługujemy sami
  contents.on('before-input-event', (event, input) => {
    if (input.type !== 'keyDown') return
    const ctrl = input.control || input.meta
    const key = input.key.toLowerCase()
    let handled = true
    if (input.key === 'F11') mainWindow.setFullScreen(!mainWindow.isFullScreen())
    else if (input.key === 'Escape' && mainWindow.isFullScreen()) mainWindow.setFullScreen(false)
    else if (input.key === 'F5' || (ctrl && key === 'r')) contents.reload()
    else if (ctrl && (key === '=' || key === '+')) contents.setZoomLevel(Math.min(contents.getZoomLevel() + 0.5, 3))
    else if (ctrl && key === '-') contents.setZoomLevel(Math.max(contents.getZoomLevel() - 0.5, -3))
    else if (ctrl && key === '0') contents.setZoomLevel(0)
    else if (allowDevTools && (input.key === 'F12' || (ctrl && input.shift && key === 'i'))) contents.toggleDevTools()
    else handled = false
    if (handled) event.preventDefault()
  })

  if (smokeShot !== undefined) runSmokeTest(mainWindow, smokeShot)

  mainWindow.on('closed', () => { mainWindow = null })
  mainWindow.loadURL(devUrl || `${ORIGIN}/index.html`)
}

// --- test uruchomienia dla CI ---

function runSmokeTest(win, shotPath) {
  const contents = win.webContents
  const errors = []
  const finish = (code, message) => {
    console.log(`[smoke-test] ${message}`)
    for (const error of errors) console.log(`[smoke-test] błąd strony: ${error}`)
    app.exit(code)
  }
  const timer = setTimeout(() => finish(4, 'przekroczony czas'), 30000)

  contents.on('console-message', (...args) => {
    // Electron 3x+: jeden argument ze szczegółami; starsze: (event, level, message)
    const details = args.length === 1 ? args[0] : { level: args[1], message: args[2] }
    const level = details.level
    if (level === 3 || level === 'error') errors.push(details.message)
  })
  contents.on('render-process-gone', (event, details) => finish(2, `proces strony padł: ${details.reason}`))
  contents.on('did-fail-load', (event, code, description, url) => finish(3, `nie wczytano ${url}: ${description}`))
  contents.on('did-finish-load', async () => {
    // chwila na zamontowanie Vue i wczytanie czcionek
    await new Promise(resolve => setTimeout(resolve, 2500))
    const result = await contents.executeJavaScript(`({
      menu: !!document.querySelector('.start-screen'),
      gods: document.querySelectorAll('.god-option').length,
      app: !!(window.orlog && window.orlog.app),
      version: window.orlog && window.orlog.version,
      title: document.title
    })`)
    if (shotPath) {
      const image = await contents.capturePage()
      require('node:fs').writeFileSync(shotPath, image.toPNG())
    }
    clearTimeout(timer)
    // błędy połączenia z serwerem są w teście normalne (serwera nie ma), wyjątki w kodzie już nie
    const fatal = errors.filter(e => /Uncaught|SyntaxError|TypeError|ReferenceError/.test(e))
    const ok = result.menu && result.app && fatal.length === 0
    finish(ok ? 0 : 1, `${ok ? 'OK' : 'BŁĄD'} ${JSON.stringify(result)}`)
  })
}

// --- start ---

ipcMain.on('orlog:info', event => {
  event.returnValue = { version: app.getVersion(), platform: process.platform }
})

// jedna kopia aplikacji: drugie uruchomienie pokazuje istniejące okno
if (smokeShot === undefined && !app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (!mainWindow) return
    if (mainWindow.isMinimized()) mainWindow.restore()
    mainWindow.focus()
  })

  app.whenReady().then(() => {
    Menu.setApplicationMenu(null)
    serveDist()
    createWindow()
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
  })

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })
}
