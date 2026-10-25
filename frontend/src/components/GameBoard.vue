<template>
  <div class="game-container">
    <PlayerMenu v-if="!playerName" :error="joinError" @name-submitted="submitName" />

    <div v-else class="game-interface">
      <transition name="toast">
        <div v-if="errorMessage" class="error-toast" @click="errorMessage = ''">
          {{ errorMessage }}
        </div>
      </transition>

      <!-- Opponent Section - Fixed at top -->
      <div class="section opponent-section">
        <OpponentSection 
          :opponent="opponent"
        />
      </div>

      <!-- Neutral Zone - Center with fixed height -->
      <div class="section neutral-section">
        <NeutralZone
          :stage="data.stage"
          :active-player="data.active_player"
          :winner="data.winner"
          :round="data.round"
          :log="data.log || []"
          :opponent="opponent"
          :player="player"
          @new-game="newGame"
        />
      </div>

      <!-- Player Section - Fixed at bottom -->
      <div class="section player-section">
        <PlayerSection
          :player="player"
          :can-select-dice="canSelectDice"
          :can-select-god="canSelectGod"
          :selected-dice-indexes="selectedDiceIndexes"
          @toggle-die-selection="toggleDieSelection"
          @confirm-dice="confirmDice"
          @choose-god="chooseGod"
          @skip-god="skipGod"
        />
      </div>
    </div>
  </div>
</template>

<script>
import socket from '../socket';
import PlayerMenu from './PlayerMenu.vue';
import OpponentSection from './OpponentSection.vue';
import NeutralZone from './NeutralZone.vue';
import PlayerSection from './PlayerSection.vue';

export default {
  components: {
    PlayerMenu,
    OpponentSection,
    NeutralZone,
    PlayerSection
  },
  data() {
    return {
      playerName: '',
      data: {},
      selectedDiceIndexes: [],
      joinError: '',
      errorMessage: '',
      errorTimer: null
    }
  },
  computed: {
    player() {
      return this.data.players?.find(p => p.name === this.playerName) || {}
    },
    opponent() {
      return this.data.players?.find(p => p.name !== this.playerName) || {}
    },
    isMyTurn() {
      return this.data.active_player === this.playerName
    },
    stage() {
      return this.data.stage
    },
    canSelectDice() {
      return this.isMyTurn && this.stage === 'dice';
    },
    canSelectGod() {
      return this.isMyTurn && this.stage === 'gods';
    }
  },
  mounted() {
    socket.on('connect', () => {
      console.log('Połączono z serwerem Socket.IO');
      // po reconnecie socket ma nowe ID, więc dołączamy jeszcze raz z tą samą nazwą
      if (this.playerName) {
        socket.emit('submit_player_name', this.playerName);
      }
    });

    socket.on('game_state', (data) => {
      this.data = data
    });

    socket.on('join_rejected', (message) => {
      this.playerName = '';
      this.data = {};
      this.joinError = message;
    });

    socket.on('error_message', (message) => {
      this.selectedDiceIndexes = [];
      this.showError(message);
    });
  },
  beforeUnmount() {
    socket.off('connect');
    socket.off('game_state');
    socket.off('join_rejected');
    socket.off('error_message');
    clearTimeout(this.errorTimer);
  },
  methods: {
    submitName(name) {
      this.joinError = '';
      this.playerName = name;
      socket.emit('submit_player_name', name);
    },
    showError(message) {
      this.errorMessage = message;
      clearTimeout(this.errorTimer);
      this.errorTimer = setTimeout(() => { this.errorMessage = '' }, 4000);
    },
    toggleDieSelection(index) {
      const pos = this.selectedDiceIndexes.indexOf(index)
      if (pos >= 0) this.selectedDiceIndexes.splice(pos, 1)
      else this.selectedDiceIndexes.push(index)
    },
    confirmDice() {
      if (!this.canSelectDice) return;

      let selectedDice;

      if (this.player.rzuty === 1) {
        selectedDice = this.player.rolled_dice.slice();
        this.selectedDiceIndexes = this.player.rolled_dice.map((_, i) => i);
      } else {
        selectedDice = this.player.rolled_dice.filter((_, i) =>
          this.selectedDiceIndexes.includes(i)
        );
      }

      this.player.saved_dice.push(...selectedDice);
      this.player.rolled_dice = this.player.rolled_dice.filter((_, i) =>
        !this.selectedDiceIndexes.includes(i)
      );

      socket.emit('confirm_dice', {
        player: this.playerName,
        selectedIndexes: this.selectedDiceIndexes
      });

      this.selectedDiceIndexes = [];
    },
    chooseGod({ godName, level }) {
      if (!this.canSelectGod) return;

      const god = this.player.gods.find(g => g.name === godName);
      if (god) {
        this.player.chosen_god = {
          ...god,
          level
        };
      }
      socket.emit('choose_god', {
        player: this.playerName,
        godName,
        level
      });
    },
    skipGod() {
      if (!this.canSelectGod) return;
      socket.emit('choose_god', {
        player: this.playerName,
        godName: null,
        level: null
      });
    },
    newGame() {
      socket.emit('new_game');
    }
  }
}
</script>

<style scoped>
/* Sekcje mają wysokość swojej zawartości. Jak ekran jest za niski, strona się przewija,
   zamiast ucinać kości i przyciski. */
.game-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.game-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.error-toast {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  padding: 0.6rem 1.2rem;
  background: #c62828;
  color: #fff;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  cursor: pointer;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}

.section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0.5rem 1rem;
  box-sizing: border-box;
}

.opponent-section {
  flex: 0 0 auto;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 2px solid #dee2e6;
}

/* środek zajmuje to, co zostaje z wysokości ekranu */
.neutral-section {
  flex: 1 0 auto;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border-bottom: 2px solid #dee2e6;
}

.player-section {
  flex: 0 0 auto;
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
}

@media (max-width: 600px) {
  .section {
    padding: 0.5rem;
  }
}
</style>