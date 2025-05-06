<template>
    <div class="game-container">
      <h1>Orlog Online</h1>
  
      <button @click="joinGame">Dołącz do gry</button>
      <button @click="rollDice">Rzuć kośćmi</button>
  
      <div v-if="store.dice.length">
        <h2>Wynik rzutu:</h2>
        <div class="dice-list">
          <span v-for="(face, index) in store.dice" :key="index">{{ face }}</span>
        </div>
  
        <h3>Wybierz bóstwo:</h3>
        <div class="god-buttons">
          <button @click="useGod('Thor')">Thor ⚡ (Atak)</button>
          <button @click="useGod('Frigg')">Frigg 💧 (Leczenie)</button>
          <button @click="useGod('Tyr')">Tyr 🛡️ (Obrona)</button>
        </div>
      </div>
  
      <div v-if="store.selectedGod">
        <p>Wybrane bóstwo: <strong>{{ store.selectedGod }}</strong></p>
      </div>
  
      <div v-if="store.players.length">
        <h4>Gracze w pokoju:</h4>
        <ul>
          <li v-for="p in store.players" :key="p">{{ p }}</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { io } from 'socket.io-client'
  import { onMounted } from 'vue'
  import { useGameStore } from '../stores/counter.js'
  
  const store = useGameStore()
  const socket = io('http://localhost:5000')  // Adres backendu
  const room = 'room1'  // Identyfikator pokoju
  
  onMounted(() => {
    socket.on('player_joined', (data) => {
      store.players = data.players
    })
  
    socket.on('dice_result', (data) => {
      store.dice = data.dice
    })
  
    socket.on('god_power_used', (data) => {
      alert(`Gracz ${data.sid} użył mocy: ${data.god}`)
    })
  })
  
  function joinGame() {
    socket.emit('join_game', { room })
  }
  
  function rollDice() {
    socket.emit('roll_dice', { room })
  }
  
  function useGod(god) {
    store.selectedGod = god
    socket.emit('use_god_power', { room, god })
  }
  </script>
  
  <style scoped>
  .game-container {
    max-width: 600px;
    margin: auto;
    text-align: center;
    font-family: sans-serif;
    padding: 1rem;
  }
  
  .dice-list span {
    display: inline-block;
    padding: 0.5rem;
    margin: 0.3rem;
    background: #f0f0f0;
    border-radius: 5px;
    font-weight: bold;
  }
  
  .god-buttons button {
    margin: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    background-color: #ececec;
    cursor: pointer;
    font-weight: bold;
  }
  
  .god-buttons button:hover {
    background-color: #ddd;
  }
  </style>
  