<template>
  <div id="app">
    <GameBoard :socket="socket" :game="game" :sid="sid" :room="room"/>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { io } from 'socket.io-client'
import GameBoard from './components/GameBoard.vue'

const socket = io('http://localhost:5000')
const game = ref({
  room: 'game_room_1',
  players: {},
  current_turn: null,
  dice: [],
  hp: {},
  mana: {},
  round: 1,
})

const sid = ref('QqcjB5myFsAquX_dAAAB') // SID gracza
const room = ref('game_room_1') // Pokój gry

onMounted(() => {
  socket.on('game_update', (data) => {
    game.value = data
    console.log('[GAME_UPDATE]', game.value)
  })

  socket.emit('join_room', { room: room.value, client_id: sid.value })
})
</script>

<style>
/* Style globalne */
#app {
  font-family: 'Arial', sans-serif;
  text-align: center;
}
</style>
