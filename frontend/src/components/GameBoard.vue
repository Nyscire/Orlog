<template>
  <div>
    <h2>Gra Orlog Online</h2>

    <div v-if="!connected">
      <p>Łączenie z serwerem...</p>
    </div>

    <div v-else>
      <p>Twoje ID: {{ socketId }}</p>
      <p>Obecna tura: {{ gameState.current_turn }}</p>

      <div class="players">
        <div v-for="player in gameState.players" :key="player.sid" :style="{ margin: '10px', padding: '10px', border: '1px solid #ccc' }">
          <h3>{{ player.sid === socketId ? 'Ty' : 'Przeciwnik' }}</h3>
          <p>HP: {{ player.hp }}</p>
          <p>Mana: {{ player.mana }}</p>
          <p>Statystyki tymczasowe:</p>
          <ul>
            <li v-for="(val, key) in player.temp_stats" :key="key">{{ key }}: {{ val }}</li>
          </ul>
        </div>
      </div>

      <div style="margin-top: 20px;">
        <button :disabled="!canRoll" @click="rollDice">Rzuć kośćmi</button>
        <button :disabled="!canAttack" @click="attack">Atakuj</button>
      </div>
    </div>
  </div>
</template>

<script>
import { io } from "socket.io-client";

export default {
  data() {
    return {
      socket: null,
      socketId: null,
      gameState: {
        players: [],
        current_turn: null,
      },
      connected: false,
      hasRolledDice: false,
      room: 'game_room_1'
    };
  },
  computed: {
    me() {
      return this.gameState.players.find(p => p.sid === this.socketId) || {};
    },
    canRoll() {
      return this.socketId && this.socketId === this.gameState.current_turn && !this.hasRolledDice;
    },
    canAttack() {
      return this.socketId && this.socketId === this.gameState.current_turn && this.hasRolledDice;
    }
  },
  methods: {
    rollDice() {
      if (!this.canRoll) return;
      this.socket.emit("roll_dice", { room: this.room });
    },
    attack() {
      if (!this.canAttack) return;
      this.socket.emit("attack", { room: this.room });
    },
    joinGame() {
      this.socket.emit("join_game", { room: this.room });
    }
  },
  mounted() {
    this.socket = io("http://localhost:5000");
    
    this.socket.on("connect", () => {
      this.socketId = this.socket.id;
      this.connected = true;
      this.joinGame();
      console.log("Connected with socketId:", this.socketId);
    });

    this.socket.on("game_update", (data) => {
      this.gameState = data;
      this.hasRolledDice = false;

      const me = data.players.find(p => p.sid === this.socketId);
      if (me && me.temp_stats) {
        const rolled = Object.values(me.temp_stats).some(v => v > 0);
        this.hasRolledDice = rolled;
      }

      console.log("Game update:", data);
    });

    this.socket.on("dice_result", (result) => {
      console.log("Kości:", result);
    });

    this.socket.on("error", (err) => {
      console.error("Błąd:", err.message);
    });
  }
};
</script>

<style scoped>
button[disabled] {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
