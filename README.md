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

Konta graczy i wyniki partii zapisują się w `backend/orlog.db` (zob. „Konta i ranking”).

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
npm run dist:win     # instalator i przenośny .exe (też na Linuksie)
npm run wydanie -- 1.0.1   # nowa wersja dla graczy, zob. „Wydanie nowej wersji”
```

Adres serwera aplikacja bierze z ustawień gry. Uruchomiona z kodu (`npm run app`) od razu łączy się z serwerem na tym samym komputerze (`127.0.0.1:5000`). Zainstalowana bez wbudowanego adresu otwiera ustawienia przy pierwszym starcie. Domyślny adres można wbudować przy budowaniu: `VITE_BACKEND_URL=https://orlog.example.com npm run dist`. Bez numeru portu gra łączy się z portem 5000 (`1.2.3.4` → `http://1.2.3.4:5000`), a `localhost` zamienia na `127.0.0.1`, bo serwer domyślnie słucha tylko na IPv4.

Drugi gracz na tym samym komputerze: „Nowe okno” w stopce menu, przycisk w ustawieniach, skrót Ctrl+Shift+N albo ponowne uruchomienie aplikacji. Każde takie okno to osobny gracz z własną, tymczasową pamięcią (bez sesji i imienia z pierwszego okna). Ustawienia wyglądu i adres serwera kopiuje z okna, z którego je otwarto.

Skróty w aplikacji: F11 to pełny ekran, Ctrl + plus/minus/0 to powiększenie, a F5 albo Ctrl+R przeładowanie. Narzędzia deweloperskie (F12) są w wersji z `npm run app`, a w zainstalowanej po uruchomieniu z `--devtools`. Jeśli na Ubuntu aplikacja z `npm run app` nie startuje z błędem o „SUID sandbox”, uruchom ją przez `npm run app -- --no-sandbox`.

### Wydanie nowej wersji

Wydanie robi się z własnego komputera, bez GitHub Actions:

```bash
cd frontend
npm run wydanie -- 1.0.1
```

Skrypt (`frontend/scripts/wydanie.mjs`) ustawia wersję w `package.json` i buduje wszystkie pliki: na Linuksie AppImage, `.deb`, instalator i przenośny `.exe`. Potem wrzuca je do wydania `v1.0.1` w zakładce Releases i od razu je publikuje. Pliki trafiają najpierw do szkicu, więc gracze widzą wydanie dopiero z kompletem plików. Na koniec skrypt przypomina, żeby zapisać nowy numer wersji (`git commit` i `git push`).

- `npm run wydanie` bez numeru bierze wersję z `package.json`.
- `--szkic` zostawia wydanie jako szkic, żeby obejrzeć je przed „Publish release”.
- `--bez-wysylania` tylko buduje do `frontend/release/`.

Numer musi być wyższy niż w ostatnim wydaniu, bo aplikacje pobierają tylko nowsze wersje; skrypt sprawdza to przed budowaniem. Tag wydania wskazuje na ostatni commit, więc najlepiej najpierw zrobić `git push`. Na Windowsie skrypt zbuduje tylko pliki na Windowsa.

Do wysyłania potrzebny jest jednorazowo dostęp do repozytorium na GitHubie:
- najprościej przez [GitHub CLI](https://cli.github.com/): `sudo apt install gh`, a potem `gh auth login`,
- albo token: GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens, dostęp do repozytorium Orlog z uprawnieniem „Contents: Read and write”. Potem `export GH_TOKEN=...` przed `npm run wydanie`.

Wine nie jest potrzebne. Zwykle electron-builder na Linuksie uruchamia przez Wine pomocniczy program, który tworzy deinstalator do instalatora `.exe`. Tutaj `scripts/electron-builder.mjs` podsuwa mu zamiast Wine `scripts/nsis-bez-wine.cjs`, który wyciąga deinstalator prosto z pliku, tak samo jak electron-builder robi to na macOS. Wszystkie `npm run dist*` idą przez ten skrypt. Gdyby kiedyś trzeba było prawdziwego Wine, wystarczy ustawić `USE_SYSTEM_WINE=true`.

Adres serwera wbudowany w aplikację ustawia plik `frontend/.env.production.local` (nie trafia do repo):

```
VITE_BACKEND_URL=https://orlog.example.com
```

Skrypt przed budowaniem wypisuje, jaki adres trafi do aplikacji. Bez tego pliku gracz wpisuje adres w ustawieniach przy pierwszym starcie.

Workflow `.github/workflows/build.yml` niczego nie wydaje, tylko sprawdza każdy PR i push na `main`:
- uruchamia testy serwera, buduje obraz Dockera i sprawdza, czy serwer w kontenerze odpowiada,
- buduje aplikację na Linuksie (bez Wine) tak samo jak `npm run wydanie` i uruchamia ją na próbę (zwykłą i AppImage),
- na Windowsie instaluje zbudowany na Linuksie instalator, uruchamia zainstalowaną grę i przenośny `.exe`, a na końcu odinstalowuje grę,
- sprawdza, czy aplikacja znajduje i pobiera aktualizację (udawane wydanie 99.0.0 na lokalnym serwerze).

### Aktualizacje

Zainstalowana aplikacja przy starcie i co godzinę sprawdza, czy na GitHubie jest nowsze wydanie (electron-updater, kod w `frontend/electron/updater.cjs`):
- instalator na Windowsa i AppImage: nowa wersja pobiera się w tle, a potem w rogu okna pojawia się pasek „Nowa wersja … jest gotowa” z przyciskiem „Uruchom ponownie”. Bez kliknięcia instaluje się przy zamknięciu gry. Po ponownym uruchomieniu gracz wraca do swojego stołu.
- paczka `.deb`: też pobiera się w tle, a „Zainstaluj” pyta o hasło (instalacja pakietu w systemie).
- przenośny `.exe` nie potrafi się podmienić, więc pasek pokazuje tylko „Pobierz” z linkiem do strony z wydaniami.
- aplikacja uruchomiona z kodu (`npm run app`) niczego nie sprawdza.

Aplikacje widzą tylko opublikowane wydania (szkic jeszcze nie). Do aktualizacji potrzebują plików `latest.yml` i `latest-linux.yml`, które `npm run wydanie` wysyła razem z instalatorami.

### Jeden plik do wysłania

Bez instalacji, np. dla znajomego:
- Windows: `Orlog-1.0.0-portable.exe`. Uruchamia się dwuklikiem; pierwsze uruchomienie trwa kilka sekund dłużej, bo plik się rozpakowuje.
- Linux: `Orlog-1.0.0.AppImage`. Wystarczy nadać prawo do uruchamiania (`chmod +x Orlog-1.0.0.AppImage` albo we właściwościach pliku) i kliknąć. Na Ubuntu 24.04 i nowszych AppImage może nie wystartować przez ograniczenia AppArmor; wtedy `./Orlog-1.0.0.AppImage --no-sandbox` albo instalacja z `.deb`.

Oba pliki powstają razem z instalatorami (`npm run dist:win`, `npm run dist:linux`), a `npm run wydanie` wrzuca je do wydania na GitHubie. Plik to tylko aplikacja: znajomy musi mieć dostęp do serwera gry. Adres wbudowany przy budowaniu (`VITE_BACKEND_URL`, np. w `frontend/.env.production.local`) sprawia, że nic nie musi wpisywać; bez niego wpisuje adres w ustawieniach przy pierwszym starcie.

Instalatory nie są podpisane, więc Windows przy pierwszym uruchomieniu pokaże ostrzeżenie SmartScreen („Więcej informacji” → „Uruchom mimo to”). Na Linuksie najprościej zainstalować `.deb` (`sudo apt install ./Orlog-1.0.0.deb`); AppImage wymaga biblioteki `libfuse2`.

## Serwer w internecie

Serwer trzyma stoły w pamięci, więc zawsze działa jako jeden proces (`--workers 1`), a połączenia graczy obsługują wątki. Konta i wyniki partii są w pliku bazy SQLite (zob. „Konta i ranking”). Port 5000 musi być otwarty w zaporze. `GET /health` zwraca stan serwera (liczbę stołów i graczy).

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

- Przed grą każdy wpisuje imię (albo się loguje), wybiera do 3 z 20 bogów, a potem zakłada stół albo dosiada się do wolnego stołu z listy. Partia zaczyna się, gdy przy stole siedzi dwóch graczy.
- Gracze na zmianę rzucają kośćmi i odkładają te, które chcą zatrzymać. Każdy ma 3 rzuty, w ostatnim zostają wszystkie kości.
- Po rzutach liczy się mana: każda kość z monetą w rogu daje 1 manę, a każda ręka kradnie przeciwnikowi 1 manę (jeśli ją ma).
- Potem każdy wybiera łaskę boga (albo ją pomija). Frigg i Loki wskazują kości na stole, a Odyn i Tyr ile HP poświęcić.
- Walka: najpierw łaski „przed walką” (zmiany kości), potem atakuje gracz kierujący, po nim drugi, a na końcu łaski „po walce” (obrażenia, leczenie, mana). Tarcze blokują strzały, hełmy blokują topory. Kradzież Thryma działa jeszcze przed zapłatą za łaskę przeciwnika i obniża jej poziom.
- W kolejnej rundzie kieruje drugi gracz. Gra kończy się, gdy ktoś spadnie do 0 HP, i można od razu zagrać rewanż.

W środku planszy jest dziennik z przebiegiem każdej rundy: jakie kości mają gracze, jakie łaski wybrali, co zrobiły łaski i jak poszedł atak. Przycisk „Jak grać?” (w menu i na planszy) otwiera krótkie zasady z opisem każdej kości.

## Stoły

Serwer prowadzi wiele partii naraz, każdą przy osobnym stole (do 50 stołów). W menu po prawej jest lista stołów: najpierw te z wolnym miejscem (przycisk „Dosiądź się”), potem trwające partie. Stół można nazwać, a bez nazwy wyświetla się jako „Stół gracza X”. Każdy stół ma czteroznakowy kod, widoczny też na planszy. Imię gracza jest unikalne na całym serwerze, a gość nie może zająć loginu zarejestrowanego gracza.

- Po odświeżeniu strony gra sama wraca na twoje miejsce: przy siadaniu serwer daje token, który zostaje w przeglądarce. Otwarcie gry w drugiej karcie przenosi miejsce do nowej karty.
- „Wstań od stołu” kończy partię. Przeciwnik zostaje przy stole i czeka na nowego rywala, a stół znów pojawia się na liście jako wolny.
- Jeśli przeciwnik się rozłączy, na górze planszy pojawia się informacja i można poczekać na jego powrót albo wstać od stołu.
- Stół, przy którym czeka rozłączony gracz, znika z listy od razu i zwalnia się po 30 s. Partia, w której obaj gracze są offline, jest usuwana po 5 minutach.

Stołami zarządza `TableManager` w `backend/tables.py` (bez Socket.IO, więc łatwo go testować). `backend/main.py` tylko tłumaczy zdarzenia Socket.IO na jego metody. Każdy stół to pokój Socket.IO, więc stan gry dostają tylko gracze przy tym stole, a listę stołów wszyscy.

Zdarzenia od klienta: `get_tables`, `create_table {name, gods, table_name, ranked}`, `join_table {table, name, gods}`, `resume {name, token}`, `leave_table`, a w trakcie gry `confirm_dice`, `choose_god`, `new_game`. Serwer wysyła `tables`, `seated {name, token, table}`, `game_state` (z polami `table`, `notice` i `result`), `join_rejected`, `resume_failed`, `seat_lost` i `error_message`.

## Konta i ranking

Konto jest opcjonalne. Gość wpisuje imię i gra jak dotąd, ale tylko partie normalne i nic mu się nie zapisuje. Konto zakłada się w menu („Załóż konto”): login (widzą go inni), e-mail (tylko do odzyskania hasła) i hasło. Zalogowany gracz:

- gra pod swoim loginem, a w menu widzi swój ranking,
- może zakładać stoły rankingowe i do nich dosiadać (przełącznik „Normalna / Rankingowa” nad nazwą stołu); na liście takie stoły mają złotą plakietkę i ranking graczy,
- ma profil („Profil” w menu): bilans wygranych i przegranych (osobno rankingowe i normalne), ranking i miejsce, najwyższy ranking, statystyki bogów (ile partii każdym i jak często wygrywa) i historię partii z przeciwnikiem, wynikiem, HP i bogami obu stron,
- widzi ranking wszystkich graczy („Ranking” w stopce menu); z rankingu i historii można przejść do profilu innego gracza.

Zapisują się wszystkie partie, w których gra choć jedno konto. Ranking (Elo, start 1000, K = 32) zmieniają tylko partie rankingowe: wygrana z mocniejszym rywalem daje więcej punktów, a zmianę widać na planszy po końcu partii. W partii rankingowej wyjście od stołu w trakcie gry to przegrana walkowerem, a jeśli przeciwnik rozłączy się i nie wróci w ciągu minuty, wygrywasz walkowerem. Partia, w której obaj gracze są offline, przepada bez wyniku.

Zapomniane hasło: „Nie pamiętasz hasła?” w oknie logowania wysyła na e-mail konta sześciocyfrowy kod ważny 15 minut. Po wpisaniu kodu i nowego hasła gracz jest od razu zalogowany, a stare sesje na innych urządzeniach się kończą.

### Po stronie serwera

Konta i partie są w bazie SQLite (`backend/db.py`, schemat i migracje), plik wskazuje zmienna `ORLOG_DB` (domyślnie `backend/orlog.db`). W Dockerze baza leży w wolumenie `orlog-data` (`/data/orlog.db`), a w usłudze systemd w `/var/lib/orlog/orlog.db`. Kopia zapasowa: `sqlite3 orlog.db ".backup kopia.db"` albo skopiowanie pliku przy zatrzymanym serwerze.

Hasła są zapisane jako skrót scrypt, a sesje jako skrót tokenu, więc z samej bazy nie da się zalogować na cudze konto. Po 10 błędnych hasłach konto jest blokowane na 15 minut. Hasło idzie do serwera tym samym połączeniem co gra, więc na serwerze dostępnym z internetu warto mieć HTTPS (Caddy, zob. niżej).

Kody do resetu hasła wysyła serwer pocztowy ustawiony zmiennymi środowiskowymi:

| zmienna | znaczenie |
| --- | --- |
| `ORLOG_SMTP_HOST` | serwer SMTP, np. `smtp.gmail.com` |
| `ORLOG_SMTP_PORT` | domyślnie 587 (465 przy `ssl`) |
| `ORLOG_SMTP_SECURITY` | `starttls` (domyślnie), `ssl` albo `none` |
| `ORLOG_SMTP_USER`, `ORLOG_SMTP_PASSWORD` | login i hasło do skrzynki (w Gmailu hasło do aplikacji) |
| `ORLOG_SMTP_FROM` | nadawca, domyślnie `ORLOG_SMTP_USER` |

W Dockerze są w `deploy/docker-compose.yml` (zakomentowane), a w systemd w pliku `/etc/orlog.env`. Bez `ORLOG_SMTP_HOST` mail z kodem trafia do logu serwera (`docker compose logs orlog` albo `journalctl -u orlog`), więc można przekazać kod graczowi samemu.

Kod: `backend/accounts.py` (rejestracja, logowanie, sesje, reset hasła), `backend/stats.py` (zapis partii, Elo, profil, ranking), `backend/mailer.py` (poczta). `TableManager` nie wie nic o bazie: dostaje funkcję zapisu skończonej partii (`recorder`) i funkcję sprawdzającą zajęte loginy (`reserved`). Aplikacja trzyma token sesji w `localStorage` i wysyła go przy każdym połączeniu Socket.IO (`auth`), więc po odświeżeniu gracz od razu jest zalogowany. Zdarzenia: `register`, `login`, `logout`, `reset_request`, `reset_confirm`, `get_profile`, `get_history`, `get_ranking`; serwer odpowiada `account`, `account_error`, `reset_sent`, `profile`, `history` i `ranking`.

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
