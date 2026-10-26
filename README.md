# Orlog

Gra w kości dla dwóch osób na podstawie minigry z AC:Valhalla. Backend we Flasku (Flask-SocketIO), frontend w Vue 3 + Vite, aplikacja na komputer w Electronie.

Gra ma dwie części: serwer (stoły i partie) i klienta (aplikacja albo strona w przeglądarce). Serwer stoi w jednym miejscu, np. na VPS-ie, a gracze łączą się z nim z aplikacji.

## Jak odpalić u siebie

Backend (port 5000):

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Frontend w przeglądarce:

```bash
cd frontend
npm install
npm run dev
```

Żeby grać z kimś w tej samej sieci, odpal frontend z `npm run dev -- --host`. W przeglądarce frontend łączy się z backendem na tym samym hoście na porcie 5000. Inny adres można wpisać w ustawieniach gry (sekcja „Serwer gry”) albo na stałe w `frontend/.env.local`:

```
VITE_BACKEND_URL=http://192.168.0.10:5000
```

## Aplikacja (Electron)

Ten sam frontend w oknie aplikacji, bez przeglądarki. Pliki są w `frontend/electron/` (`main.cjs` otwiera okno, `preload.cjs` przekazuje stronie wersję aplikacji).

```bash
cd frontend
npm install
npm run app          # buduje frontend i otwiera go w oknie aplikacji
npm run app:dev      # okno z serwerem Vite (w drugim terminalu: npm run dev), zmiany widać od razu
npm run dist         # instalator na system, na którym budujesz (wyniki w frontend/release/)
npm run dist:linux   # AppImage i .deb
npm run dist:win     # instalator .exe (najprościej budować na Windowsie albo w GitHub Actions)
```

Adres serwera aplikacja bierze z ustawień gry. Uruchomiona z kodu (`npm run app`) od razu łączy się z serwerem na tym samym komputerze (`127.0.0.1:5000`). Zainstalowana bez wbudowanego adresu otwiera ustawienia przy pierwszym starcie. Domyślny adres można wbudować przy budowaniu: `VITE_BACKEND_URL=https://orlog.example.com npm run dist`. Bez numeru portu gra łączy się z portem 5000 (`1.2.3.4` → `http://1.2.3.4:5000`), a `localhost` zamienia na `127.0.0.1`, bo serwer domyślnie słucha tylko na IPv4.

Drugi gracz na tym samym komputerze: „Nowe okno” w stopce menu, przycisk w ustawieniach, skrót Ctrl+Shift+N albo ponowne uruchomienie aplikacji. Każde takie okno to osobny gracz z własną, tymczasową pamięcią (bez sesji i imienia z pierwszego okna). Ustawienia wyglądu i adres serwera kopiuje z okna, z którego je otwarto.

Skróty w aplikacji: F11 to pełny ekran, Ctrl + plus/minus/0 to powiększenie, a F5 albo Ctrl+R przeładowanie. Narzędzia deweloperskie (F12) są w wersji z `npm run app`, a w zainstalowanej po uruchomieniu z `--devtools`. Jeśli na Ubuntu aplikacja z `npm run app` nie startuje z błędem o „SUID sandbox”, uruchom ją przez `npm run app -- --no-sandbox`.

### Instalatory z GitHuba

Workflow `.github/workflows/build.yml` przy każdym PR i pushu na `main`:
- uruchamia testy serwera, buduje obraz Dockera i sprawdza, czy serwer w kontenerze odpowiada,
- buduje aplikację na Windowsie i Linuksie, uruchamia ją na próbę (zrzut ekranu jest w artefaktach) i zapisuje instalatory jako artefakty.

Wydanie: `git tag v1.0.0 && git push origin v1.0.0` (numer zgodny z `version` w `frontend/package.json`). Instalatory trafiają do szkicu wydania w zakładce Releases; wystarczy go opublikować. Adres serwera wbudowany w instalatory ustawia zmienna repozytorium `ORLOG_SERVER_URL` (Settings → Secrets and variables → Actions → Variables).

Instalatory nie są podpisane, więc Windows przy pierwszym uruchomieniu pokaże ostrzeżenie SmartScreen („Więcej informacji” → „Uruchom mimo to”). Na Linuksie najprościej zainstalować `.deb` (`sudo apt install ./Orlog-1.0.0.deb`); AppImage wymaga biblioteki `libfuse2`.

## Serwer w internecie

Serwer trzyma stoły w pamięci, więc zawsze działa jako jeden proces (`--workers 1`), a połączenia graczy obsługują wątki. Port 5000 musi być otwarty w zaporze. `GET /health` zwraca stan serwera (liczbę stołów i graczy).

Najprościej w Dockerze (z katalogu głównego repo):

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

Bez Dockera, np. na Ubuntu w `/opt/orlog`:

```bash
sudo useradd --system orlog
sudo git clone https://github.com/Nyscire/Orlog.git /opt/orlog
sudo python3 -m venv /opt/orlog/venv
sudo /opt/orlog/venv/bin/pip install -r /opt/orlog/backend/requirements.txt
sudo cp /opt/orlog/deploy/orlog.service /etc/systemd/system/
sudo systemctl enable --now orlog
```

W aplikacji wpisuje się wtedy adres serwera, np. `1.2.3.4` albo `http://1.2.3.4:5000`. Z domeną można dodać HTTPS przez Caddy (`deploy/Caddyfile`): Caddy sam pobiera certyfikat i przekazuje połączenia do gry, a w aplikacji adres to `https://orlog.example.com`.

## Zasady w skrócie

- Przed grą każdy wpisuje imię, wybiera do 3 z 20 bogów, a potem zakłada stół albo dosiada się do wolnego stołu z listy. Partia zaczyna się, gdy przy stole siedzi dwóch graczy.
- Gracze na zmianę rzucają kośćmi i odkładają te, które chcą zatrzymać. Każdy ma 3 rzuty, w ostatnim zostają wszystkie kości.
- Po rzutach liczy się mana: każda kość z monetą w rogu daje 1 manę, a każda ręka kradnie przeciwnikowi 1 manę (jeśli ją ma).
- Potem każdy wybiera łaskę boga (albo ją pomija). Frigg i Loki wskazują kości na stole, a Odyn i Tyr ile HP poświęcić.
- Walka: najpierw łaski „przed walką” (zmiany kości), potem atakuje gracz kierujący, po nim drugi, a na końcu łaski „po walce” (obrażenia, leczenie, mana). Tarcze blokują strzały, hełmy blokują topory. Kradzież Thryma działa jeszcze przed zapłatą za łaskę przeciwnika i obniża jej poziom.
- W kolejnej rundzie kieruje drugi gracz. Gra kończy się, gdy ktoś spadnie do 0 HP, i można od razu zagrać rewanż.

W środku planszy jest dziennik z przebiegiem każdej rundy: jakie kości mają gracze, jakie łaski wybrali, co zrobiły łaski i jak poszedł atak. Przycisk „Jak grać?” (w menu i na planszy) otwiera krótkie zasady z opisem każdej kości.

## Stoły

Serwer prowadzi wiele partii naraz, każdą przy osobnym stole (do 50 stołów). W menu po prawej jest lista stołów: najpierw te z wolnym miejscem (przycisk „Dosiądź się”), potem trwające partie. Stół można nazwać, a bez nazwy wyświetla się jako „Stół gracza X”. Każdy stół ma czteroznakowy kod, widoczny też na planszy. Imię gracza jest unikalne na całym serwerze.

- Po odświeżeniu strony gra sama wraca na twoje miejsce: przy siadaniu serwer daje token, który zostaje w przeglądarce. Otwarcie gry w drugiej karcie przenosi miejsce do nowej karty.
- „Wstań od stołu” kończy partię. Przeciwnik zostaje przy stole i czeka na nowego rywala, a stół znów pojawia się na liście jako wolny.
- Jeśli przeciwnik się rozłączy, na górze planszy pojawia się informacja i można poczekać na jego powrót albo wstać od stołu.
- Stół, przy którym czeka rozłączony gracz, znika z listy od razu i zwalnia się po 30 s. Partia, w której obaj gracze są offline, jest usuwana po 5 minutach.

Stołami zarządza `TableManager` w `backend/tables.py` (bez Socket.IO, więc łatwo go testować). `backend/main.py` tylko tłumaczy zdarzenia Socket.IO na jego metody. Każdy stół to pokój Socket.IO, więc stan gry dostają tylko gracze przy tym stole, a listę stołów wszyscy.

Zdarzenia od klienta: `get_tables`, `create_table {name, gods, table_name}`, `join_table {table, name, gods}`, `resume {name, token}`, `leave_table`, a w trakcie gry `confirm_dice`, `choose_god`, `new_game`. Serwer wysyła `tables`, `seated {name, token, table}`, `game_state` (z polami `table` i `notice`), `join_rejected`, `resume_failed`, `seat_lost` i `error_message`.

## Ustawienia

W menu i na planszy (ikona zębatki) są ustawienia: język (polski albo angielski), sześć motywów kolorów (w tym dwa ciemne: „Noc polarna” i „Otchłań Hel”), trzy zestawy czcionek i większy tekst. Zapisują się w przeglądarce. Każdy gracz może grać w swoim języku, bo serwer wysyła dziennik i błędy jako kody, a zdania tworzy frontend.

- teksty: `frontend/src/locales/pl.js` i `en.js` (te same klucze); nowy język to kolejny plik plus wpis w `LANGUAGES` w `settings.js` i w `messages` w `i18n.js`
- motywy i czcionki: `frontend/src/assets/theme.css` (zmienne kolorów dla każdego `data-theme`, czcionki dla `data-font`)

## Bogowie

Lista bogów, koszty i wartości łask są wzięte z [wiki Assassin's Creed](https://assassinscreed.fandom.com/wiki/Orlog). Każda łaska to osobna klasa w `backend/god.py` z polami:

- `effect` – klucz łaski (np. `thor_strike`), po nim frontend dobiera nazwę, opis i wpis w dzienniku (`FAVORS` w `frontend/src/locales/pl.js` i `en.js`),
- `phase` – kiedy działa: `first` (Thrym), `before` (przed atakami) albo `after` (po atakach),
- `order` – kolejność w fazie, gdy obaj gracze mają łaski z tej samej fazy,
- `needs` – dodatkowy wybór gracza: `amount` (ile HP), `opponent_dice` albo `any_dice` (które kości).

Nowy bóg to klasa z metodą `apply(ctx)` i wpis w `god_factory()`. Ikona idzie do `frontend/public/img/gods/<imię małymi literami>.svg`, a polskie imię (jeśli inne niż angielskie) do `GOD_NAMES` w `locales/pl.js`. Liczbę bogów na gracza ustawia `GODS_PER_PLAYER` w `backend/game.py`.

## Testy

```bash
cd backend
python -m unittest discover -s tests -t .
```

Czcionki Cinzel, Grenze Gotisch, Alegreya, Atkinson Hyperlegible Next i Noto Sans Runic (tylko znaki runiczne) są na licencji SIL Open Font License (pliki `*-OFL.txt` w `frontend/src/assets/fonts`).

Ikony bogów i ręki pochodzą z [game-icons.net](https://game-icons.net) (licencja [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)), autorzy: Lorc, Delapouite i Caro Asercion. Kolor zmieniony na potrzeby gry.
