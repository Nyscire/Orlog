<template>
  <div class="game-container">
    <StartMenu
      v-if="!inGame"
      :lobby="lobby"
      :connected="connected"
      :joined="!!playerName"
      :player-name="playerName"
      :chosen-gods="chosenGods"
      :error="errorText(joinError)"
      :notice="errorText(notice)"
      @join="join"
      @leave="leaveLobby"
      @help="showHelp = true"
      @settings="showSettings = true"
    />

    <!-- v-else musi stać zaraz po StartMenu, inaczej dowiąże się do innego v-if -->
    <div v-else class="game-interface">
      <transition name="toast">
        <div v-if="errorMessage" class="error-toast" @click="errorMessage = ''">
          {{ errorText(errorMessage) }}
        </div>
      </transition>

      <div v-if="!connected" class="status-banner warn">
        {{ $t('board.selfOffline') }}
      </div>
      <div v-else-if="opponentOffline" class="status-banner">
        <span><strong>{{ opponent.name }}</strong> {{ $t('board.opponentOffline') }}</span>
        <button class="btn btn-gold banner-btn" @click="leaveGame">{{ $t('board.endGame') }}</button>
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
          :pick="canSelectGod ? pick : null"
          @toggle-target="toggleTarget"
          @new-game="newGame"
          @help="showHelp = true"
          @settings="showSettings = true"
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
          :pick="canSelectGod ? pick : null"
          @toggle-die-selection="toggleDieSelection"
          @confirm-dice="confirmDice"
          @choose-god="chooseGod"
          @skip-god="skipGod"
          @select-favor="selectFavor"
          @favor-amount="setFavorAmount"
        />
      </div>
    </div>

    <HelpDialog v-if="showHelp" @close="showHelp = false" />
    <SettingsDialog v-if="showSettings" @close="showSettings = false" />
  </div>
</template>

<script>
import socket from '../socket';
import StartMenu from './StartMenu.vue';
import HelpDialog from './HelpDialog.vue';
import SettingsDialog from './SettingsDialog.vue';
import { errorText } from '../i18n';
import OpponentSection from './OpponentSection.vue';
import NeutralZone from './NeutralZone.vue';
import PlayerSection from './PlayerSection.vue';

export default {
  components: {
    StartMenu,
    HelpDialog,
    SettingsDialog,
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
      showSettings: false,
      selectedDiceIndexes: [],
      // łaska wybierana w fazie bogów: { god, name, level, needs, max, amount, own, opponent }
      pick: null,
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
  watch: {
    // po swojej turze w fazie bogów zaczynamy wybór od nowa
    canSelectGod(value) {
      if (!value) this.pick = null
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
    // błędy i komunikaty z serwera przychodzą jako kody; tłumaczymy je przy wyświetlaniu
    errorText(error) {
      return errorText(error);
    },
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
      this.pick = null;
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
    selectFavor({ god, level }) {
      const same = this.pick && this.pick.name === god.name
      const max = god.values?.[level - 1] || 0
      const pick = {
        god,
        name: god.name,
        level,
        needs: god.needs || null,
        max,
        amount: same ? this.pick.amount : 1,
        own: same ? [...this.pick.own] : [],
        opponent: same ? [...this.pick.opponent] : []
      }
      // niższy poziom pozwala wskazać mniej kości
      while (pick.own.length + pick.opponent.length > max) {
        if (pick.opponent.length) pick.opponent.pop()
        else pick.own.pop()
      }
      this.pick = pick
    },
    setFavorAmount(value) {
      if (!this.pick) return
      const max = Math.max((this.player.HP || 0) - 1, 1)
      this.pick.amount = Math.max(1, Math.min(value, max))
    },
    toggleTarget({ side, index }) {
      const pick = this.pick
      if (!pick || !pick.level) return
      if (pick.needs !== 'any_dice' && !(pick.needs === 'opponent_dice' && side === 'opponent')) return
      const list = pick[side]
      const pos = list.indexOf(index)
      if (pos >= 0) {
        list.splice(pos, 1)
      } else if (pick.own.length + pick.opponent.length < pick.max) {
        list.push(index)
      } else if (pick.max === 1) {
        // przy jednej kości kliknięcie innej po prostu zmienia wybór
        pick.own = []
        pick.opponent = []
        pick[side].push(index)
      }
    },
    chooseGod({ godName, level }) {
      if (!this.canSelectGod) return;

      const god = this.player.gods.find(g => g.name === godName);
      const payload = { player: this.playerName, godName, level };
      const pick = this.pick && this.pick.name === godName ? this.pick : null;
      if (pick && pick.needs === 'amount') payload.amount = pick.amount;
      if (pick && pick.needs === 'opponent_dice') payload.targets = { opponent: [...pick.opponent] };
      if (pick && pick.needs === 'any_dice') payload.targets = { own: [...pick.own], opponent: [...pick.opponent] };
      if (god) {
        this.player.chosen_god = { ...god, level };
      }
      socket.emit('choose_god', payload);
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
  color: var(--on-accent);
  background: var(--gold-bright);
  border-bottom: 1px solid var(--gold-dark);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
  text-align: center;
}

.status-banner.warn {
  color: var(--on-strong);
  background: var(--blood);
  border-bottom-color: rgba(0, 0, 0, 0.3);
}

.banner-btn {
  padding: 0.3rem 0.9rem;
  font-size: 0.85rem;
  color: var(--ink);
  background: var(--card);
}

.error-toast {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  padding: 0.6rem 1.2rem;
  background: var(--blood);
  color: var(--on-strong);
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
  color: var(--on-bg);
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.15));
  border-bottom: 1px solid rgba(var(--accent-rgb), 0.35);
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