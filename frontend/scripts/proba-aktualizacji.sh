#!/usr/bin/env bash
# Test aktualizacji dla CI (z katalogu frontend, po zbudowaniu do release/).
# Udaje nowsze wydanie: te same pliki, ale wersja 99.0.0 w latest*.yml, na serwerze pod 127.0.0.1,
# i sprawdza, czy zainstalowana aplikacja je znajdzie i pobierze (main.cjs, --update-test).
#
#   scripts/proba-aktualizacji.sh latest-linux.yml xvfb-run -a release/Orlog-1.0.0.AppImage
#   scripts/proba-aktualizacji.sh latest.yml "$ORLOG_EXE"
set -euo pipefail

yml=$1
shift

rm -rf update-feed
mkdir update-feed
sed 's/^version: .*/version: 99.0.0/' "release/$yml" > "update-feed/$yml"
grep -E '^ *(- )?url:|^path:' "update-feed/$yml" | sed 's/.*: *//' | sort -u | while read -r file; do
  cp "release/$file" update-feed/
done
ls update-feed

python=$(command -v python || command -v python3)
"$python" -m http.server 8099 --bind 127.0.0.1 --directory update-feed > update-feed.log 2>&1 &
server=$!
trap 'kill "$server" 2>/dev/null || true' EXIT
sleep 2

ORLOG_UPDATE_URL=http://127.0.0.1:8099 "$@" --update-test --disable-gpu
