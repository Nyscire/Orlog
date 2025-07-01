<template>
  <div class="game-container">
    <PlayerMenu v-if="!playerName" @name-submitted="submitName" />

    <div v-else class="game-interface">
      <!-- Opponent Section -->
      <OpponentSection 
        :opponent="opponent"
        class="board-section-padding"
      />

      <!-- Neutral Zone -->
      <NeutralZone
        :stage="data.stage"
        :active-player="data.active_player"
        :opponent="opponent"
        :player="player"
        class="board-section-padding"
      />

      <!-- Player Section -->
      <PlayerSection
        :player="player"
        :can-select-dice="canSelectDice"
        :can-select-god="canSelectGod"
        :selected-dice-indexes="selectedDiceIndexes"
        @toggle-die-selection="toggleDieSelection"
        @confirm-dice="confirmDice"
        @choose-god="chooseGod"
        class="board-section-padding"
      />
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
      selectedDiceIndexes: []
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
    });

    socket.on('game_state', (data) => {
      this.data = data
    });
  },
  methods: {
    submitName(name) {
      this.playerName = name;
      socket.emit('submit_player_name', name);
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
        // Jeśli rzuty = 1, zatwierdź wszystkie kości
        selectedDice = this.player.rolled_dice.slice();
        this.selectedDiceIndexes = this.player.rolled_dice.map((_, i) => i);
      } else {
        // normalnie zatwierdź tylko wybrane kości
        selectedDice = this.player.rolled_dice.filter((_, i) =>
          this.selectedDiceIndexes.includes(i)
        );
      }

      // Dodaj zatwierdzone kości do zapisanych
      this.player.saved_dice.push(...selectedDice);

      // Usuń zatwierdzone kości z rzutu
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
    }
  }
}
</script>

<style scoped>
.game-container {
  padding: 1rem;
}

.board-section-padding {
  padding-left: 1rem;
  padding-right: 1rem;
}
</style>