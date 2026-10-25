<template>
  <div class="game-container">
    <StartMenu
      v-if="!inGame"
      :lobby="lobby"
      :connected="connected"
      :joined="!!playerName"
      :player-name="playerName"
      :chosen-gods="chosenGods"
      :error="joinError"
      :notice="notice"
      @join="join"
      @leave="leaveLobby"
      @help="showHelp = true"
    />

    <!-- v-else musi stać zaraz po StartMenu, inaczej dowiąże się do innego v-if -->
    <div v-else class="game-interface">
      <transition name="toast">
        <div v-if="errorMessage" class="error-toast" @click="errorMessage = ''">
          {{ errorMessage }}
        </div>
      </transition>

      <div v-if="!connected" class="status-banner warn">
        Utracono połączenie z serwerem. Próbuję połączyć ponownie…
      </div>
      <div v-else-if="opponentOffline" class="status-banner">
        <span>
          <strong>{{ opponent.name }}</strong> jest offline. Gra poczeka, aż przeciwnik wróci pod tym samym imieniem.
          Możesz też zakończyć partię.
        </span>
        <button class="btn btn-gold banner-btn" @click="leaveGame">Zakończ partię</button>
      </div>

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
          @help="showHelp = true"
          @leave="leaveGame"
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

    <HelpDialog v-if="showHelp" @close="showHelp = false" />
  </div>
</template>

<script>
import socket from '../socket';
import StartMenu from './StartMenu.vue';
import HelpDialog from './HelpDialog.vue';
import OpponentSection from './OpponentSection.vue';
import NeutralZone from './NeutralZone.vue';
import PlayerSection from './PlayerSection.vue';

export default {
  components: {
    StartMenu,
    HelpDialog,
    OpponentSection,
    NeutralZone,
    PlayerSection
  },
  data() {
    return {
      playerName: '',
      chosenGods: [],
      data: {},
      lobby: null,
      connected: socket.connected,
      showHelp: false,
      selectedDiceIndexes: [],
      joinError: '',
      notice: '',
      errorMessage: '',
      errorTimer: null
    }
  },
  computed: {
    // menu startowe znika dopiero, gdy obaj gracze są w grze
    inGame() {
      return !!this.playerName && !!this.data.stage && this.data.stage !== 'waiting'
    },
    opponentOffline() {
      return this.opponent.connected === false
    },
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
      this.connected = true;
      // po reconnecie socket ma nowe ID, więc dołączamy jeszcze raz z tą samą nazwą
      if (this.playerName) {
        socket.emit('submit_player_name', { name: this.playerName, gods: this.chosenGods });
      }
    });

    socket.on('disconnect', () => {
      this.connected = false;
    });

    socket.on('lobby', (lobby) => {
      this.lobby = lobby;
    });

    // połączenie mogło się zestawić, zanim komponent się zamontował
    if (socket.connected) {
      socket.emit('get_lobby');
    }

    socket.on('game_state', (data) => {
      this.data = data
    });

    socket.on('join_rejected', (message) => {
      this.playerName = '';
      this.data = {};
      this.joinError = message;
    });

    // przeciwnik zakończył partię: wracamy do menu z informacją
    socket.on('game_ended', (message) => {
      this.resetToMenu();
      this.notice = message;
    });

    socket.on('error_message', (message) => {
      this.selectedDiceIndexes = [];
      this.showError(message);
    });
  },
  beforeUnmount() {
    socket.off('connect');
    socket.off('disconnect');
    socket.off('lobby');
    socket.off('game_state');
    socket.off('join_rejected');
    socket.off('game_ended');
    socket.off('error_message');
    clearTimeout(this.errorTimer);
  },
  methods: {
    join({ name, gods }) {
      this.joinError = '';
      this.notice = '';
      this.playerName = name;
      this.chosenGods = gods;
      socket.emit('submit_player_name', { name, gods });
    },
    leaveLobby() {
      socket.emit('leave_lobby');
      this.resetToMenu();
    },
    leaveGame() {
      socket.emit('leave_game');
      this.resetToMenu();
    },
    resetToMenu() {
      this.playerName = '';
      this.data = {};
      this.selectedDiceIndexes = [];
      this.notice = '';
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

.status-banner {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  color: var(--ink);
  background: var(--gold-bright);
  border-bottom: 1px solid var(--gold-dark);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
  text-align: center;
}

.status-banner.warn {
  color: var(--parchment);
  background: var(--blood);
  border-bottom-color: rgba(0, 0, 0, 0.3);
}

.banner-btn {
  padding: 0.3rem 0.9rem;
  font-size: 0.85rem;
  background: var(--parchment);
}

.error-toast {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  padding: 0.6rem 1.2rem;
  background: var(--blood);
  color: var(--parchment);
  border: 1px solid rgba(0, 0, 0, 0.3);
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
  padding: 0.4rem 1rem;
  box-sizing: border-box;
}

/* przeciwnik na ciemnym pasie, środek i gracz na pergaminie */
.opponent-section {
  flex: 0 0 auto;
  color: var(--parchment);
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.15));
  border-bottom: 1px solid rgba(201, 162, 76, 0.35);
}

/* środek zajmuje to, co zostaje z wysokości ekranu */
.neutral-section {
  flex: 1 0 auto;
}

.player-section {
  flex: 0 0 auto;
  padding-top: 0;
}

@media (max-width: 600px) {
  .section {
    padding: 0.5rem;
  }
}
</style>