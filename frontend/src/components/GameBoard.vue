<template>
  <div class="game-container">
    <PlayerMenu v-if="!playerName" @name-submitted="submitName" />

    <div v-else class="game-interface">
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
          :opponent="opponent"
          :player="player"
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
    }
  }
}
</script>

<style scoped>
.game-container {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.game-interface {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0.75rem 1rem;
  box-sizing: border-box;
}

.opponent-section {
  height: 30vh;
  min-height: 200px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 2px solid #dee2e6;
}

.neutral-section {
  height: 40vh;
  min-height: 280px;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border-bottom: 2px solid #dee2e6;
  overflow: hidden;
}

.player-section {
  height: 30vh;
  min-height: 200px;
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
}

/* Responsive adjustments for smaller desktop screens */
@media (max-height: 800px) {
  .section {
    padding: 0.5rem 1rem;
  }
  
  .opponent-section {
    min-height: 180px;
  }
  
  .neutral-section {
    min-height: 240px;
  }
  
  .player-section {
    min-height: 180px;
  }
}

@media (max-height: 700px) {
  .section {
    padding: 0.25rem 1rem;
  }
  
  .opponent-section {
    min-height: 160px;
  }
  
  .neutral-section {
    min-height: 200px;
  }
  
  .player-section {
    min-height: 160px;
  }
}
</style>