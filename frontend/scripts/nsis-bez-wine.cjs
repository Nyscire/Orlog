// Udawane "wine" dla electron-buildera na Linuksie (podstawia je scripts/electron-builder.mjs).
//
// Instalator NSIS zawiera deinstalator, a ten powstaje tak: electron-builder buduje najpierw
// pomocniczy instalator, którego jedynym zadaniem jest zapisanie deinstalatora, i uruchamia go.
// Na Linuksie robi to przez Wine. Na macOS zamiast uruchamiać, wyciąga deinstalator prosto z pliku
// (UninstallerReader z app-builder-lib) i tu robimy dokładnie to samo, więc Wine nie jest potrzebne.
const fs = require('node:fs')
const path = require('node:path')
const { UninstallerReader } = require('app-builder-lib/out/targets/nsis/nsisUtil')

async function main() {
  const args = process.argv.slice(2)
  const installer = args[0]
  // electron-builder woła Wine (przy naszych ustawieniach) tylko w tym jednym miejscu
  if (args.length !== 1 || !/\.exe$/i.test(installer)) {
    throw new Error(`nieoczekiwane wywołanie wine: ${args.join(' ')}`)
  }
  // ta sama ścieżka, którą electron-builder wpisuje do pomocniczego instalatora (NsisTarget.ts)
  const uninstaller = path.join(path.dirname(installer), `${path.basename(installer, 'exe')}__uninstaller.exe`)
  await UninstallerReader.exec(installer, uninstaller)
  if (!fs.existsSync(uninstaller) || fs.statSync(uninstaller).size === 0) {
    throw new Error(`nie powstał deinstalator ${uninstaller}`)
  }
}

main().catch(error => {
  console.error(`[bez wine] ${error && error.message}`)
  process.exit(1)
})
