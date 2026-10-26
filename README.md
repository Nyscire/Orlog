# Orlog

Gra w kości dla dwóch osób na podstawie minigry z AC:Valhalla. Backend we Flasku (Flask-SocketIO), frontend w Vue 3 + Vite.

## Jak odpalić

Backend (port 5000):

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Żeby grać z kimś w tej samej sieci, odpal frontend z `npm run dev -- --host`. Frontend łączy się z backendem na tym samym hoście na porcie 5000. Jak backend stoi gdzie indziej, ustaw adres w `frontend/.env.local`:

```
VITE_BACKEND_URL=http://192.168.0.10:5000
```

## Zasady w skrócie

- Przed grą każdy wpisuje imię i wybiera do 3 z 20 bogów, których łaski będzie mógł użyć w partii.
- Gracze na zmianę rzucają kośćmi i odkładają te, które chcą zatrzymać. Każdy ma 3 rzuty, w ostatnim zostają wszystkie kości.
- Po rzutach liczy się mana: każda kość ze złotą obwódką daje 1 manę, a każda ręka kradnie przeciwnikowi 1 manę (jeśli ją ma).
- Potem każdy wybiera łaskę boga (albo ją pomija). Frigg i Loki wskazują kości na stole, a Odyn i Tyr ile HP poświęcić.
- Walka: najpierw łaski „przed walką” (zmiany kości), potem atakuje gracz kierujący, po nim drugi, a na końcu łaski „po walce” (obrażenia, leczenie, mana). Tarcze blokują strzały, hełmy blokują topory. Kradzież Thryma działa jeszcze przed zapłatą za łaskę przeciwnika i obniża jej poziom.
- W kolejnej rundzie kieruje drugi gracz. Gra kończy się, gdy ktoś spadnie do 0 HP, i można od razu zagrać rewanż.

W środku planszy jest dziennik z przebiegiem każdej rundy: jakie kości mają gracze, jakie łaski wybrali, co zrobiły łaski i jak poszedł atak. Przycisk „Jak grać?” (w menu i na planszy) otwiera krótkie zasady z opisem każdej kości.

Po odświeżeniu strony wystarczy wpisać tę samą nazwę, żeby wrócić do gry. Jeśli przeciwnik się rozłączy, na górze planszy pojawia się informacja i można poczekać na jego powrót albo zakończyć partię. Przycisk „Opuść grę” kończy partię dla obu graczy i wraca do menu. Serwer obsługuje jedną grę naraz.

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

Czcionki Cinzel, Grenze Gotisch, Alegreya i Atkinson Hyperlegible Next są na licencji SIL Open Font License (pliki `*-OFL.txt` w `frontend/src/assets/fonts`).

Ikony bogów i ręki pochodzą z [game-icons.net](https://game-icons.net) (licencja [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)), autorzy: Lorc, Delapouite i Caro Asercion. Kolor zmieniony na potrzeby gry.
