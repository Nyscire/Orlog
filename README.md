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

W środku planszy jest dziennik: kto co odłożył, jakie łaski wybrał, ile many dostał i ile zadał obrażeń.

Po odświeżeniu strony wystarczy wpisać tę samą nazwę, żeby wrócić do gry. Serwer obsługuje jedną grę naraz.

## Dodawanie bogów

Nowy bóg to klasa w `backend/god.py` (metoda `activate`, która coś robi i zwraca opis do dziennika) i wpis w `god_factory()`. Ikona idzie do `frontend/public/img/icons/<nazwa małymi literami>.png`. Menu startowe pobiera listę bogów z serwera, więc nowy bóg pojawi się tam sam. Liczbę bogów na gracza ustawia `GODS_PER_PLAYER` w `backend/game.py`.

## Testy

```bash
cd backend
python -m unittest discover -s tests -t .
```

Czcionka nagłówków to Cinzel (SIL Open Font License, `frontend/src/assets/fonts/Cinzel-OFL.txt`).
