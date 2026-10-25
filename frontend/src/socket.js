// src/socket.js
import { io } from 'socket.io-client';

// Adres backendu Flask. Domyślnie ten sam host co strona, port 5000,
// więc gra działa też w sieci lokalnej (np. http://192.168.0.10:5173).
// Można go nadpisać zmienną VITE_BACKEND_URL w pliku .env.local.
const backendUrl =
  import.meta.env.VITE_BACKEND_URL ||
  `${window.location.protocol}//${window.location.hostname}:5000`;

const socket = io(backendUrl);

export default socket;
