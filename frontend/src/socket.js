// src/socket.js
import { io } from 'socket.io-client';
import { serverUrl } from './server';

// Adres serwera wybiera server.js (ustawienia, VITE_BACKEND_URL albo host strony).
// Zmiana adresu w ustawieniach przeładowuje okno, więc tu wystarczy jedno połączenie.
export const currentServer = serverUrl();

// bez adresu (aplikacja bez wbudowanego serwera) nie łączymy się, dopóki gracz go nie poda
const socket = currentServer ? io(currentServer) : io({ autoConnect: false });

export default socket;
