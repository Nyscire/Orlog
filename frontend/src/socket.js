// src/socket.js
import { io } from 'socket.io-client';
import { serverUrl } from './server';
import { loadToken } from './accountToken';

// Adres serwera wybiera server.js (ustawienia, VITE_BACKEND_URL albo host strony).
// Zmiana adresu w ustawieniach przeładowuje okno, więc tu wystarczy jedno połączenie.
export const currentServer = serverUrl();

// token konta czytamy przy każdym (ponownym) połączeniu, bo gracz mógł się w międzyczasie zalogować
const options = { auth: cb => cb({ token: loadToken() || null }) };

// bez adresu (aplikacja bez wbudowanego serwera) nie łączymy się, dopóki gracz go nie poda
const socket = currentServer ? io(currentServer, options) : io({ ...options, autoConnect: false });

export default socket;
