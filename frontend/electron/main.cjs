// Aplikacja Orlog w Electronie: okno z frontendem Vue, który łączy się z serwerem gry.
//
//   npm run app                       zbudowany frontend (dist/) w oknie aplikacji
//   npm run app:dev                   okno z serwerem deweloperskim Vite (npm run dev w drugim terminalu)
//   electron . --smoke-test[=plik]    test uruchomienia dla CI: sprawdza menu, robi zrzut ekranu i wychodzi
//
// Ctrl+Shift+N albo ponowne uruchomienie aplikacji otwiera kolejne okno jako osobny gracz
// (własna, tymczasowa pamięć), np. żeby zagrać samemu ze sobą na jednym komputerze.
const { app, BrowserWindow, Menu, ipcMain, net, protocol, screen, session, shell } = require('electron')
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

function serveDist(ses) {
  ses.protocol.handle(SCHEME, async request => {
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

// --- okna ---

let mainWindow = null
let playerCount = 1
// ustawienia przekazywane nowemu oknu gracza (motyw, język, adres serwera), po id webContents
const seeds = new Map()

function createWindow({ player = 1, partition, seed } = {}) {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  const extra = player > 1
  const title = extra ? `Orlog · gracz ${player}` : 'Orlog'
  if (partition) serveDist(session.fromPartition(partition))

  const win = new BrowserWindow({
    width: Math.min(extra ? 1366 : 1440, width),
    height: Math.min(extra ? 800 : 900, height),
    minWidth: 1024,
    minHeight: 640,
    title,
    backgroundColor: '#2a1d14',
    icon: path.join(__dirname, '..', 'build', 'icon.png'),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      partition,
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
      spellcheck: false
    }
  })
  const contents = win.webContents
  seeds.set(contents.id, { player, seed: seed || null, packaged: app.isPackaged })
  // preload działa też dla pustej strony, którą okno ma przed wczytaniem gry,
  // więc ustawienia oddajemy aż do pierwszego pełnego wczytania strony gry
  contents.once('did-finish-load', () => {
    const entry = seeds.get(contents.id)
    if (entry) entry.seed = null
  })

  win.once('ready-to-show', () => {
    // na laptopach (np. 1366×768) główne okno od razu na cały ekran roboczy
    if (!extra && (width <= 1440 || height <= 900)) win.maximize()
    if (smokeShot === undefined) win.show()
  })

  // dodatkowe okna zostają podpisane numerem gracza, choć strona ustawia swój tytuł
  if (extra) {
    contents.on('page-title-updated', event => {
      event.preventDefault()
      win.setTitle(title)
    })
  }

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
    if (input.key === 'F11') win.setFullScreen(!win.isFullScreen())
    else if (input.key === 'Escape' && win.isFullScreen()) win.setFullScreen(false)
    else if (input.key === 'F5' || (ctrl && key === 'r')) contents.reload()
    else if (ctrl && input.shift && key === 'n') openPlayerWindow(contents)
    else if (ctrl && (key === '=' || key === '+')) contents.setZoomLevel(Math.min(contents.getZoomLevel() + 0.5, 3))
    else if (ctrl && key === '-') contents.setZoomLevel(Math.max(contents.getZoomLevel() - 0.5, -3))
    else if (ctrl && key === '0') contents.setZoomLevel(0)
    else if (allowDevTools && (input.key === 'F12' || (ctrl && input.shift && key === 'i'))) contents.toggleDevTools()
    else handled = false
    if (handled) event.preventDefault()
  })

  if (!extra && smokeShot !== undefined) runSmokeTest(win, smokeShot)

  win.on('closed', () => {
    seeds.delete(contents.id)
    if (win === mainWindow) mainWindow = null
  })
  win.loadURL(devUrl || `${ORIGIN}/index.html`)
  return win
}

// Nowe okno = nowy gracz: osobna pamięć (bez sesji przy stole i imienia z pierwszego okna),
// ale te same ustawienia wyglądu i ten sam serwer.
async function openPlayerWindow(fromContents) {
  let seed = null
  const source = fromContents || (mainWindow && mainWindow.webContents)
  if (source && !source.isDestroyed()) {
    try {
      seed = JSON.parse(await source.executeJavaScript(
        "JSON.stringify({ 'orlog.settings': localStorage.getItem('orlog.settings'), 'orlog.server': localStorage.getItem('orlog.server') })"))
    } catch (e) {
      seed = null
    }
  }
  playerCount += 1
  const win = createWindow({ player: playerCount, partition: `gracz-${playerCount}`, seed })
  // trochę obok poprzedniego okna, żeby było widać, że to drugie
  const from = source && BrowserWindow.fromWebContents(source)
  if (from && !from.isMaximized()) {
    const [x, y] = from.getPosition()
    win.setPosition(x + 40, y + 40)
  }
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
  const extra = seeds.get(event.sender.id) || {}
  event.returnValue = {
    version: app.getVersion(),
    platform: process.platform,
    packaged: app.isPackaged,
    player: extra.player || 1,
    seed: extra.seed || null
  }
})

ipcMain.on('orlog:new-window', event => openPlayerWindow(event.sender))

// jedna kopia aplikacji; ponowne uruchomienie otwiera w niej okno kolejnego gracza
if (smokeShot === undefined && !app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (!mainWindow) {
      mainWindow = createWindow()
      return
    }
    openPlayerWindow(mainWindow.webContents)
  })

  app.whenReady().then(() => {
    Menu.setApplicationMenu(null)
    serveDist(session.defaultSession)
    mainWindow = createWindow()
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) mainWindow = createWindow()
    })
  })

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })
}
