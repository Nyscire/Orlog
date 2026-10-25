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

- Przed grą każdy wpisuje imię i wybiera do 3 bogów, których łaski będzie mógł użyć w partii.
- Gracze na zmianę rzucają kośćmi i odkładają te, które chcą zatrzymać. Każdy ma 3 rzuty, w ostatnim zostają wszystkie kości.
- Potem każdy wybiera łaskę boga (albo ją pomija). Łaska kosztuje manę, liczy się mana zebrana wcześniej i ta z odłożonych kości.
- Walka: najpierw działają łaski, potem atakuje gracz kierujący, a po nim drugi. Tarcze blokują strzały, hełmy blokują topory.
- W kolejnej rundzie kieruje drugi gracz. Gra kończy się, gdy ktoś spadnie do 0 HP, i można od razu zagrać rewanż.

W środku planszy jest dziennik z przebiegiem każdej rundy: jakie kości mają gracze, jakie łaski wybrali, co zrobiły łaski i jak poszedł atak. Przycisk „Jak grać?” (w menu i na planszy) otwiera krótkie zasady z opisem każdej kości.

Po odświeżeniu strony wystarczy wpisać tę samą nazwę, żeby wrócić do gry. Jeśli przeciwnik się rozłączy, na górze planszy pojawia się informacja i można poczekać na jego powrót albo zakończyć partię. Przycisk „Opuść grę” kończy partię dla obu graczy i wraca do menu. Serwer obsługuje jedną grę naraz.

## Ustawienia

W menu i na planszy (ikona zębatki) są ustawienia: język (polski albo angielski), cztery motywy kolorów, trzy zestawy czcionek i większy tekst. Zapisują się w przeglądarce. Każdy gracz może grać w swoim języku, bo serwer wysyła dziennik i błędy jako kody, a zdania tworzy frontend.

- teksty: `frontend/src/locales/pl.js` i `en.js` (te same klucze); nowy język to kolejny plik plus wpis w `LANGUAGES` w `settings.js` i w `messages` w `i18n.js`
- motywy i czcionki: `frontend/src/assets/theme.css` (zmienne kolorów dla każdego `data-theme`, czcionki dla `data-font`)

## Dodawanie bogów

Bóg to jeden wpis w `god_factory()` w `backend/god.py`, np. `God("Odin", DAMAGE, [3, 5, 8], [3, 4, 5])`. Dostępne efekty: `DAMAGE` (obrażenia dla przeciwnika), `HEAL` (leczenie) i `BONUS` (dodatkowe kości w rundzie, np. `stat="helmet"`). Opis boga i wpisy w dzienniku powstają z efektu i wartości, więc nie trzeba pisać tekstów. Ikona idzie do `frontend/public/img/icons/<nazwa małymi literami>.png`, a polską formę „łaska Odyna” można dopisać w `GOD_GENITIVE` w `locales/pl.js`. Liczbę bogów na gracza ustawia `GODS_PER_PLAYER` w `backend/game.py`.

## Testy

```bash
cd backend
python -m unittest discover -s tests -t .
```

Czcionki Cinzel, Grenze Gotisch, Alegreya i Atkinson Hyperlegible Next są na licencji SIL Open Font License (pliki `*-OFL.txt` w `frontend/src/assets/fonts`).
