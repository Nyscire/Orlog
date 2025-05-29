<template>
  <div class="game-container">
    <PlayerMenu v-if="!playerName" @name-submitted="submitName" />

    <div v-else class="game-interface">
      <!-- Oponent -->
      <div class="player-section opponent compact-layout board-section-padding">
        <div class="horizontal-group">
        <div class="actions-and-stats">
          <PlayerStats :name="opponent.name" :hp="opponent.HP" :mana="opponent.Mana" />
        </div>
          <DiceDisplay
            :dice="opponent.rolled_dice"
            title="Kości przeciwnika"
            :selectable="false"
            @toggle-selection="toggleDieSelection"
          />
          <GodsOpponentDisplay
            :gods="opponent.gods"
            :readonly="true" 
          />
        </div>
      </div>

      <!-- Strefa neutralna -->
      <div class="neutral-section board-section-padding">
        <div v-if=" data.stage==='dice'">
          <h3>Aktualny etap: Wybór kości</h3>
        </div>
        <div v-else>
          <h3>Aktualny etap: Wybór boga</h3>
        </div>
        <h3>Aktualna tura: {{ data.active_player }}</h3>
        <div class="neutral-dice">
          <div class="neutral-block">
            <h4>Kości zapisane przeciwnika</h4>
            <DiceDisplay :dice="opponent.saved_dice" title="" />
          </div>

          <div class="neutral-block">
            <h4>Wybrany bóg przeciwnika</h4>
            <GodsNeutralDisplay
              v-if="opponent.chosen_god && opponent.chosen_god.name"
              :gods="[{ ...opponent.chosen_god, selected: true }]"
              :readonly="true"
              
            />
            
          </div>

          <div class="neutral-block">
            <h4>Wybrany bóg</h4>
            <GodsNeutralDisplay
              v-if="player.chosen_god && player.chosen_god.name"
              :gods="[{ ...player.chosen_god, selected: true }]"
              :readonly="true"
            />
            
          </div>

          <div class="neutral-block">
            <h4>Kości zapisane gracza</h4>
            <DiceDisplay :dice="player.saved_dice" title="" />
          </div>
        </div>
      </div>

      <!-- Gracz -->
      <div class="player-section self compact-layout board-section-padding">
        <div class="horizontal-group">
          <div class="actions-and-stats">
            <PlayerStats :name="player.name" :hp="player.HP" :mana="player.Mana" />
          </div>

          <div class="dice-section">
            <DiceDisplay
              :dice="player.rolled_dice"
              title="Wylosowane Kości"
              :selectable="canSelectDice"
              :selected-indexes="selectedDiceIndexes"
              @toggle-selection="toggleDieSelection"
            />
            <div v-if="canSelectDice" class="confirm-dice-wrapper">
              <button class="confirm-dice-button" @click="confirmDice">Zatwierdź</button>
            </div>
          </div>

          <GodsPlayerDisplay
            :gods="player.gods"
            :readonly="!canSelectGod"
            @choose-god="chooseGod"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import socket from '../socket';
import PlayerStats from './PlayerStats.vue'
import DiceDisplay from './DiceDisplay.vue'
import GodsPlayerDisplay from './GodsPlayerDisplay.vue'
import GodsNeutralDisplay from './GodsNeutralDisplay.vue'
import GodsOpponentDisplay from './GodsOpponentDisplay.vue'
import PlayerMenu from './PlayerMenu.vue';


export default {
  components: {
    PlayerStats,
    DiceDisplay,
    GodsPlayerDisplay,
    GodsOpponentDisplay,
    GodsNeutralDisplay,
    PlayerMenu
  },
  data() {
    return {
      tempName: '',
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
      this.data=data
    });
  },
  methods: {
    submitName(name) {
    this.playerName = name;
    socket.emit('submit_player_name',  name );
}
,updateGameState(data) {
      // Aktualizacja stanu gry na podstawie otrzymanych danych
    },
    sendPlayerAction(action) {
      socket.emit('player_action', action);
    },

    toggleDieSelection(index) {
      const pos = this.selectedDiceIndexes.indexOf(index)
      if (pos >= 0) this.selectedDiceIndexes.splice(pos, 1)
      else this.selectedDiceIndexes.push(index)
    },
    confirmDice() {
  if (!this.canSelectDice) return;

  const selectedDice = this.player.rolled_dice.filter((_, i) =>
    this.selectedDiceIndexes.includes(i)
  );
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

    chooseGodLevel({ godName, level }) {
      const god = this.player.gods.find(g => g.name === godName)
      if (god) {
        god.level = level
        if (this.player.chosen_god && this.player.chosen_god.name === godName) {
          this.player.chosen_god.level = level
        }
      }
    },
    toggleStage() {
      this.data.stage = this.data.stage === 'dice' ? 'gods' : 'dice'
    }
  }
}
</script>

<style scoped>
.game-container {
  padding: 1rem;
}
.name-entry {
  text-align: center;
  margin-top: 2rem;
}
.player-section {
  margin: 1rem 0;
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: nowrap;
  gap: 1rem;
  flex-shrink: 0;
}
.board-section-padding {
  padding-left: 1rem;
  padding-right: 1rem;
}
.compact-layout {
  flex-direction: row;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 1rem;
}
.horizontal-group {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  align-items: flex-start;
  justify-content: space-around;
  width: 100%;
}
.actions-and-stats {
  flex: 0 0 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.dice-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.neutral-section {
  border: 1px solid #ccc;
  height: 361px;;
  background: #f9f9f9;
}
.neutral-dice {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  gap: 1rem;
}
.neutral-block {
  flex: 1;
  min-width: 200px;
}
.confirm-dice-wrapper {
  margin-top: 0.5rem;
  text-align: center;
}
.confirm-dice-button {
  padding: 0.5rem 1rem;
  font-weight: 600;
  cursor: pointer;
}
.debug-controls {
  margin-top: 2rem;
  text-align: center;
}
h3,h4 {
  text-align: center;
}
</style>