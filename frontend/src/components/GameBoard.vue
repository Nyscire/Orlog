<template>
  <div class="game-board">
    <div class="status-bar">
      <p><strong>Twój SID:</strong> {{ sid }}</p>
      <p><strong>Pokój:</strong> {{ game.room }}</p>
      <p><strong>Aktualna tura:</strong> {{ game.current_turn }}</p>
    </div>

    <div class="players">
      <div
        class="player"
        v-for="(player, playerId) in game.players"
        :key="playerId"
        :class="{ active: playerId === game.current_turn }"
      >
        <h3>Gracz: {{ playerId === sid ? 'Ty' : 'Przeciwnik' }}</h3>
        <p>HP: {{ game.hp[playerId] }}</p>
        <p>Mana: {{ game.mana[playerId] }}</p>
      </div>
    </div>

    <div class="dice-container">
      <h3>Wynik rzutu kostkami</h3>
      <div class="dice" v-if="game.dice && game.dice.length > 0">
        <div v-for="(die, index) in game.dice" :key="index" class="die">
          <img :src="`/img/icons/${die.stat_type}.svg`" class="dice-icon" />
          <p>{{ die.stat_type }}</p>
        </div>
      </div>
    </div>

    <div class="controls">
      <button @click="rollDice" :disabled="game.current_turn !== sid">
        Rzuć kostkami
      </button>
      <button @click="attack" :disabled="game.current_turn !== sid">
        Atakuj
      </button>
      <button @click="drainMana" :disabled="game.current_turn !== sid">
        Zmień manę
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { io } from 'socket.io-client'

const props = defineProps({
  game: Object,
  sid: String
})

const emit = defineEmits(['update-dice'])

const socket = io('http://localhost:5000')

const rollDice = () => {
  console.log('Sending roll_dice', props.game)
  socket.emit('roll_dice', { room: props.game.room, sid: props.sid })
}

const attack = () => {
  socket.emit('attack', { room: props.game.room, sid: props.sid })
}

const drainMana = () => {
  socket.emit('drain_mana', { room: props.game.room, sid: props.sid })
}

socket.on('dice_result', (data) => {
  emit('update-dice', data)
})
</script>

<style scoped>
.game-board {
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

.status-bar {
  margin-bottom: 20px;
}

.players {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.player {
  border: 1px solid #ccc;
  padding: 10px;
  width: 48%;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.player.active {
  border-color: #007bff;
  background-color: #e6f0ff;
}

.dice-container {
  margin-bottom: 20px;
  text-align: center;
}

.dice {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.die {
  text-align: center;
}

.dice-icon {
  width: 64px;
  height: 64px;
}

.controls {
  text-align: center;
  margin-top: 20px;
}

button {
  margin: 0 10px;
  padding: 10px 15px;
  font-size: 16px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
