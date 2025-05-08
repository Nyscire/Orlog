<template>
  <div class="game-board">
    <h1>Game Board</h1>
    <div v-if="game">
      <div class="game-info">
        <p><strong>Current turn:</strong> {{ game.current_turn }}</p>
        <p><strong>Round:</strong> {{ game.round }}</p>
      </div>
      <div class="dice-section">
        <button @click="rollDice" class="roll-button">Roll Dice</button>
        <div v-if="game.dice.length > 0" class="dice-result">
          <p><strong>Dice:</strong> {{ game.dice.join(', ') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  socket: Object,
  game: Object,
  sid: String,
  room: String
})

const rollDice = () => {
  if (!props.game || !props.game.room || !props.sid) {
    console.error('Missing room or sid')
    return
  }
  // Przekazywanie pełnych danych: room i client_id (sid)
  const data = {
    room: props.game.room,
    client_id: props.sid,
  }
  console.log('Sending roll_dice', data)
  props.socket.emit('roll_dice', data)
}
</script>

<style scoped>
.game-board {
  font-family: 'Arial', sans-serif;
  text-align: center;
  margin-top: 50px;
}

.game-info {
  margin-bottom: 20px;
}

.dice-section {
  margin-top: 30px;
}

.roll-button {
  padding: 12px 24px;
  font-size: 18px;
  background-color: #3498db;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.roll-button:hover {
  background-color: #2980b9;
}

.dice-result {
  margin-top: 20px;
  font-size: 18px;
  font-weight: bold;
}

h1 {
  font-size: 32px;
  margin-bottom: 20px;
  color: #2c3e50;
}
</style>
