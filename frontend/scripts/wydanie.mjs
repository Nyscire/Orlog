// Nowa wersja gry prosto z własnego komputera, bez GitHub Actions: buduje instalatory
// i wrzuca je do wydania na GitHubie, skąd biorą je aktualizacje w aplikacji.
//
//   npm run wydanie -- 1.0.1             ustawia wersję 1.0.1, buduje i publikuje wydanie v1.0.1
//   npm run wydanie                      to samo z wersją, która już jest w package.json
//   npm run wydanie -- 1.0.1 --szkic     wydanie zostaje szkicem, publikujesz je sam na GitHubie
//   npm run wydanie -- --bez-wysylania   tylko buduje wszystko do release/, nic nie wysyła
//
// Na Linuksie powstają pliki na oba systemy (AppImage, .deb, instalator i przenośny .exe),
// na Windowsie tylko te na Windowsa. Instalator na Windowsa budowany na Linuksie potrzebuje Wine
// (jednorazowo, zob. WINE_INSTALL). Do wysyłania potrzebny jest token GitHuba: zalogowane gh
// (gh auth login) albo zmienna GH_TOKEN. Adres serwera wbudowany w aplikację to VITE_BACKEND_URL
// z frontend/.env.production.local (albo ze zmiennej środowiskowej).
import { execFileSync, spawnSync } from 'node:child_process'
import fs from 'node:fs'
import http from 'node:http'
import https from 'node:https'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const RELEASE_DIR = path.join(ROOT, 'release')
const PACKAGE = path.join(ROOT, 'package.json')
const API = (process.env.GITHUB_API_URL || 'https://api.github.com').replace(/\/$/, '')
const WINDOWS = process.platform === 'win32'
const OPTIONS = ['--szkic', '--bez-wysylania']
// 32-bitowe Wine jest potrzebne na Ubuntu 24.04 i starszych; na nowszych samo "wine" też wystarczy
const WINE_INSTALL = 'sudo dpkg --add-architecture i386 && sudo apt update && sudo apt install wine wine32:i386'

function fail(message) {
  console.error(`\n✗ ${message}`)
  process.exit(1)
}

function warn(message) {
  console.log(`! ${message}`)
}

const mb = bytes => (bytes < 1024 * 1024 ? `${Math.ceil(bytes / 1024)} kB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`)
const readVersion = () => JSON.parse(fs.readFileSync(PACKAGE, 'utf8')).version

function compareVersions(a, b) {
  const pa = a.split(/[.-]/).map(n => parseInt(n, 10) || 0)
  const pb = b.split(/[.-]/).map(n => parseInt(n, 10) || 0)
  for (let i = 0; i < 3; i++) {
    if ((pa[i] || 0) !== (pb[i] || 0)) return (pa[i] || 0) - (pb[i] || 0)
  }
  return 0
}

function nextPatch(version) {
  const [major, minor, patch] = version.split(/[.-]/).map(n => parseInt(n, 10) || 0)
  return `${major}.${minor}.${patch + 1}`
}

// to samo repozytorium, z którego aplikacja pobiera aktualizacje
function readRepo() {
  const config = fs.readFileSync(path.join(ROOT, 'electron-builder.yml'), 'utf8')
  const start = config.search(/^publish:/m)
  const publish = start < 0 ? '' : config.slice(start)
  const owner = publish.match(/^\s+owner:\s*(\S+)/m)
  const repo = publish.match(/^\s+repo:\s*(\S+)/m)
  if (!owner || !repo) fail('W electron-builder.yml brakuje publish z owner i repo')
  return `${owner[1]}/${repo[1]}`
}

function findToken() {
  for (const name of ['GH_TOKEN', 'GITHUB_TOKEN']) {
    if (process.env[name]) return process.env[name].trim()
  }
  try {
    return execFileSync('gh', ['auth', 'token'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim()
  } catch (e) {
    return ''
  }
}

function hasWine() {
  try {
    execFileSync('wine', ['--version'], { stdio: 'ignore' })
    return true
  } catch (e) {
    return false
  }
}

// Pierwsze uruchomienie Wine zakłada jego katalog (~/.wine) i potrafi zapytać okienkiem o Wine Mono,
// a electron-builder czeka na Wine tylko 2 minuty. Dlatego katalog zakładamy wcześniej, bez pytań.
function prepareWine() {
  const prefix = process.env.WINEPREFIX || path.join(os.homedir(), '.wine')
  if (fs.existsSync(path.join(prefix, 'system.reg'))) return
  console.log('\nPierwsze uruchomienie Wine: zakładam jego katalog, to chwilę potrwa')
  const env = { ...process.env, WINEDEBUG: '-all', WINEDLLOVERRIDES: 'mscoree,mshtml=;winemenubuilder.exe=d' }
  const result = spawnSync('wine', ['wineboot', '--init'], { stdio: 'inherit', env })
  spawnSync('wineserver', ['-w'], { stdio: 'ignore', env })
  if (result.status !== 0) warn('wineboot zakończył się błędem, ale budowanie spróbuje dalej')
}

function git(...args) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim()
  } catch (e) {
    return null
  }
}

// adres serwera, który Vite wbuduje w aplikację (ta sama kolejność plików co w Vite)
function serverAddress() {
  if (process.env.VITE_BACKEND_URL) return process.env.VITE_BACKEND_URL
  let value = ''
  for (const name of ['.env', '.env.local', '.env.production', '.env.production.local']) {
    const file = path.join(ROOT, name)
    if (!fs.existsSync(file)) continue
    const match = fs.readFileSync(file, 'utf8').match(/^\s*VITE_BACKEND_URL\s*=\s*(.*)$/m)
    if (match) value = match[1].trim().replace(/^(['"])(.*)\1$/, '$2')
  }
  return value
}

function run(command, args, hint = '') {
  console.log(`\n$ ${[command, ...args].join(' ')}`)
  const result = spawnSync(command, args, { cwd: ROOT, stdio: 'inherit', shell: WINDOWS })
  if (result.error) fail(`Nie udało się uruchomić ${command}: ${result.error.message}`)
  if (result.status !== 0) fail(`${command} ${args[0]} zakończył się błędem (kod ${result.status})${hint ? `\n  ${hint}` : ''}`)
}

// --- GitHub ---

function request(method, url, { token, json, file, onProgress } = {}) {
  return new Promise((resolve, reject) => {
    const target = new URL(url)
    const headers = {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'orlog-wydanie'
    }
    if (token) headers.Authorization = `Bearer ${token}`
    let body = null
    if (json !== undefined) {
      body = Buffer.from(JSON.stringify(json))
      headers['Content-Type'] = 'application/json'
      headers['Content-Length'] = body.length
    } else if (file) {
      headers['Content-Type'] = 'application/octet-stream'
      headers['Content-Length'] = fs.statSync(file).size
    }
    const client = target.protocol === 'http:' ? http : https
    const req = client.request(target, { method, headers }, res => {
      const chunks = []
      res.on('data', chunk => chunks.push(chunk))
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf8')
        let data = text
        try {
          data = text ? JSON.parse(text) : null
        } catch (e) {
          // zostaje tekst
        }
        resolve({ status: res.statusCode, data })
      })
    })
    req.on('error', reject)
    if (file) {
      // duże pliki idą strumieniem, bez wczytywania całych do pamięci
      let sent = 0
      const stream = fs.createReadStream(file)
      stream.on('data', chunk => {
        sent += chunk.length
        if (onProgress) onProgress(sent)
      })
      stream.on('error', reject)
      stream.pipe(req)
    } else {
      req.end(body)
    }
  })
}

const api = (method, route, options) => request(method, `${API}${route}`, options)

function apiError(what, res) {
  const detail = res.data && res.data.message ? `: ${res.data.message}` : ''
  return `${what} (GitHub odpowiedział ${res.status}${detail})`
}

async function uploadAsset(uploadUrl, name, token) {
  const file = path.join(RELEASE_DIR, name)
  const size = fs.statSync(file).size
  const label = `  ${name} (${mb(size)})`
  const tty = process.stdout.isTTY
  let shown = -1
  const progress = sent => {
    const percent = Math.floor((sent * 100) / size)
    if (tty && percent !== shown) {
      shown = percent
      process.stdout.write(`\r${label} ${percent}%`)
    }
  }
  const res = await request('POST', `${uploadUrl}?name=${encodeURIComponent(name)}`, { token, file, onProgress: progress })
  if (res.status !== 201) {
    if (tty) process.stdout.write('\n')
    fail(`${apiError(`Nie udało się wysłać ${name}`, res)}. Uruchom npm run wydanie jeszcze raz: niedokończony szkic zostanie zastąpiony.`)
  }
  process.stdout.write(tty ? `\r${label} ok    \n` : `${label} ok\n`)
}

// --- wydanie ---

async function main() {
  const args = process.argv.slice(2)
  for (const arg of args) {
    if (arg.startsWith('--') && !OPTIONS.includes(arg)) fail(`Nieznana opcja ${arg} (są: ${OPTIONS.join(', ')})`)
  }
  const positional = args.filter(arg => !arg.startsWith('--'))
  if (positional.length > 1) fail('Podaj jeden numer wersji, np. npm run wydanie -- 1.0.1')
  const newVersion = positional[0] ? positional[0].replace(/^v/, '') : null
  if (newVersion && !/^\d+\.\d+\.\d+$/.test(newVersion)) fail(`"${positional[0]}" to nie numer wersji (ma być np. 1.0.1)`)
  const draft = args.includes('--szkic')
  const upload = !args.includes('--bez-wysylania')

  if (!fs.existsSync(path.join(ROOT, 'node_modules', 'electron-builder'))) {
    fail('Brak zależności: najpierw npm install w katalogu frontend')
  }
  if (!WINDOWS && !hasWine()) {
    fail(`Do zbudowania instalatora na Windowsa potrzebne jest Wine. Wystarczy raz zainstalować:\n  ${WINE_INSTALL}`)
  }

  const repo = readRepo()
  const version = newVersion || readVersion()
  const tag = `v${version}`
  let token = ''
  let target = ''

  // wszystko, co może nie wyjść po stronie GitHuba, sprawdzamy przed kilkuminutowym budowaniem
  if (upload) {
    token = findToken()
    if (!token) {
      fail('Brak tokenu GitHuba. Zaloguj się przez "gh auth login" albo ustaw GH_TOKEN (README, sekcja "Wydanie nowej wersji").')
    }
    const repoInfo = await api('GET', `/repos/${repo}`, { token })
    if (repoInfo.status === 401) fail('GitHub nie przyjął tokenu (wygasł albo jest błędny)')
    if (repoInfo.status !== 200) fail(apiError(`Nie widzę repozytorium ${repo}`, repoInfo))
    if (repoInfo.data.permissions && !repoInfo.data.permissions.push) fail(`To konto nie może zapisywać w ${repo}`)

    const existing = await api('GET', `/repos/${repo}/releases/tags/${tag}`, { token })
    if (existing.status === 200) {
      fail(`Wersja ${version} jest już wydana (${existing.data.html_url}). Podaj wyższy numer, np. npm run wydanie -- ${nextPatch(version)}`)
    }
    const latest = await api('GET', `/repos/${repo}/releases/latest`, { token })
    if (latest.status === 200) {
      const latestVersion = latest.data.tag_name.replace(/^v/, '')
      if (compareVersions(version, latestVersion) <= 0) {
        fail(`Ostatnie wydanie to ${latest.data.tag_name}, a aplikacje pobierają tylko wyższy numer. Np. npm run wydanie -- ${nextPatch(latestVersion)}`)
      }
    }

    // tag wydania wskazuje na commit, z którego budujemy, o ile jest już na GitHubie
    const head = git('rev-parse', 'HEAD')
    const onGithub = head && (await api('GET', `/repos/${repo}/commits/${head}`, { token })).status === 200
    target = onGithub ? head : repoInfo.data.default_branch
    if (!onGithub) warn(`Ostatniego commita nie ma jeszcze na GitHubie (git push), więc tag ${tag} wskaże na ${target}.`)
    if (git('status', '--porcelain')) warn('Masz niezapisane zmiany w repozytorium: trafią do instalatorów, ale nie do kodu na GitHubie.')
  }

  if (newVersion && newVersion !== readVersion()) {
    run('npm', ['version', newVersion, '--no-git-tag-version', '--allow-same-version'])
  }

  const server = serverAddress()
  console.log(`\nOrlog ${version}: pliki na ${WINDOWS ? 'Windowsa' : 'Linuksa i Windowsa'}`)
  console.log(server
    ? `Adres serwera w aplikacji: ${server}`
    : 'Bez wbudowanego adresu serwera: gracz wpisze go w ustawieniach (VITE_BACKEND_URL w .env.production.local)')
  if (WINDOWS) warn('Na Windowsie nie powstaną pliki na Linuksa, więc gracze z AppImage i .deb nie dostaną tej wersji.')

  if (!WINDOWS) prepareWine()
  fs.rmSync(RELEASE_DIR, { recursive: true, force: true })
  run('npm', ['run', 'build'])
  run('npx', ['electron-builder', ...(WINDOWS ? ['--win'] : ['--linux', '--win']), '--publish', 'never'],
    WINDOWS ? '' : `Jeśli wyżej jest błąd wine (przy budowaniu Orlog-Setup), doinstaluj 32-bitowe Wine:\n  ${WINE_INSTALL}`)

  const files = fs.readdirSync(RELEASE_DIR)
    .filter(name => /\.(AppImage|deb|exe|blockmap)$/.test(name) || /^latest.*\.yml$/.test(name))
    .filter(name => !name.startsWith('__') && fs.statSync(path.join(RELEASE_DIR, name)).isFile())
    .sort()
  for (const name of WINDOWS ? ['latest.yml'] : ['latest.yml', 'latest-linux.yml']) {
    if (!files.includes(name)) fail(`Brak ${name} w release/, a bez niego aplikacje nie zobaczą aktualizacji`)
  }
  console.log('\nPliki wydania:')
  for (const name of files) console.log(`  ${name} (${mb(fs.statSync(path.join(RELEASE_DIR, name)).size)})`)

  if (!upload) {
    console.log('\nGotowe, bez wysyłania. Pliki są w frontend/release/.')
    return
  }

  // niedokończony szkic tej samej wersji (np. po przerwanym wysyłaniu) zastępujemy nowym
  const releases = await api('GET', `/repos/${repo}/releases?per_page=50`, { token })
  if (releases.status === 200) {
    for (const old of releases.data.filter(r => r.draft && r.tag_name === tag)) {
      console.log(`\nUsuwam stary szkic ${tag}`)
      await api('DELETE', `/repos/${repo}/releases/${old.id}`, { token })
    }
  }

  const created = await api('POST', `/repos/${repo}/releases`, {
    token,
    json: { tag_name: tag, target_commitish: target, name: `Orlog ${version}`, draft: true, generate_release_notes: true }
  })
  if (created.status === 403) fail('Token nie może tworzyć wydań: potrzebne jest uprawnienie "Contents: Read and write" do repozytorium')
  if (created.status !== 201) fail(apiError('Nie udało się utworzyć wydania', created))
  const release = created.data
  const uploadUrl = release.upload_url.replace(/\{.*\}$/, '')

  // pliki trafiają najpierw do szkicu, a gracze widzą wydanie dopiero z kompletem plików
  console.log(`\nWysyłam na GitHuba (${tag}):`)
  for (const name of files) await uploadAsset(uploadUrl, name, token)

  if (draft) {
    console.log(`\nGotowe. Szkic wydania: ${release.html_url}`)
    console.log(`Aplikacje zobaczą wersję ${version} dopiero po kliknięciu "Publish release".`)
  } else {
    const published = await api('PATCH', `/repos/${repo}/releases/${release.id}`, {
      token,
      json: { draft: false, make_latest: 'true' }
    })
    if (published.status !== 200) fail(apiError(`Pliki są w szkicu ${release.html_url}, ale publikacja się nie udała`, published))
    console.log(`\nGotowe: ${published.data.html_url}`)
    console.log(`Zainstalowane aplikacje pobiorą wersję ${version} przy starcie albo w ciągu godziny.`)
  }
  if (newVersion) {
    console.log(`\nZapisz nowy numer wersji: git commit -m "Wersja ${version}" package.json package-lock.json && git push`)
  }
}

main().catch(error => fail(`Coś poszło nie tak: ${error && error.message}`))
