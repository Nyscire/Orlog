// electron-builder, który na Linuksie buduje instalator na Windowsa bez Wine.
// Argumenty idą prosto do electron-buildera, np.:
//
//   node scripts/electron-builder.mjs --win --publish never
//
// electron-builder potrzebuje Wine tylko do zrobienia deinstalatora w instalatorze NSIS.
// Podajemy mu własny "zestaw Wine" (ELECTRON_BUILDER_WINE_TOOLSET_DIR), w którym bin/wine
// to scripts/nsis-bez-wine.cjs: wyciąga deinstalator z pliku tak samo jak electron-builder na macOS.
// USE_SYSTEM_WINE=true wyłącza podmianę i używa prawdziwego Wine z systemu.
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const WINDOWS = process.platform === 'win32'

function fakeWineToolset() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'orlog-bez-wine-'))
  // electron-builder sprawdza, czy zestaw ma bin/wine, wine-home i lib
  for (const sub of ['bin', 'lib', 'wine-home']) fs.mkdirSync(path.join(dir, sub))
  const script = path.join(ROOT, 'scripts', 'nsis-bez-wine.cjs')
  fs.writeFileSync(path.join(dir, 'bin', 'wine'), `#!/bin/sh\nexec "${process.execPath}" "${script}" "$@"\n`, { mode: 0o755 })
  return dir
}

const env = { ...process.env }
let toolset = null
if (!WINDOWS && !env.ELECTRON_BUILDER_WINE_TOOLSET_DIR && env.USE_SYSTEM_WINE !== 'true') {
  toolset = fakeWineToolset()
  env.ELECTRON_BUILDER_WINE_TOOLSET_DIR = toolset
}

const result = spawnSync('npx', ['electron-builder', ...process.argv.slice(2)], { cwd: ROOT, stdio: 'inherit', env, shell: WINDOWS })
if (toolset) fs.rmSync(toolset, { recursive: true, force: true })
if (result.error) {
  console.error(`Nie udało się uruchomić electron-buildera: ${result.error.message}`)
  process.exit(1)
}
process.exit(result.status === null ? 1 : result.status)
