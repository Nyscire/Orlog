<template>
  <GameBoard
    v-if="game"
    :game="game"
    :sid="sid"
    @update-dice="updateDice"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { io } from 'socket.io-client'
import GameBoard from './components/GameBoard.vue'

const socket = io('http://localhost:5000')

const game = ref(null)
const sid = ref(null)

onMounted(() => {
  socket.on('connect', () => {
    sid.value = socket.id
    socket.emit('join_game', { room: 'game_room_1' })
  })

  socket.on('game_update', (data) => {
    console.log('[GAME_UPDATE]', data)
    game.value = data
  })

  socket.on('dice_result', (data) => {
    updateDice(data)
  })

  socket.on('error', (data) => {
    console.error('[ERROR]', data)
  })
})

const updateDice = (diceData) => {
  if (game.value) {
    game.value.dice = diceData
  }
}
</script>
