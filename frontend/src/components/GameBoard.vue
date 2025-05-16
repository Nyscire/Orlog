<template>
  <div class="game-container">
    <div v-if="!playerName" class="name-entry">
      <input v-model="tempName" placeholder="Podaj swoją nazwę" />
      <button @click="submitName">Zatwierdź</button>
    </div>

    <div v-else class="game-interface">
      <!-- Oponent -->
      <div class="player-section opponent compact-layout board-section-padding">
        <div class="horizontal-group">
          <PlayerStats :name="opponent.name" :hp="opponent.HP" :mana="opponent.Mana" />
          <DiceDisplay
            :dice="opponent.rolled_dice"
            title="Kości przeciwnika"
            :selectable="false"
            @toggle-selection="toggleDieSelection"
          />
          <GodsDisplay
            :gods="opponent.gods"
            :readonly="true" 
          />
        </div>
      </div>

      <!-- Strefa neutralna -->
      <div class="neutral-section board-section-padding">
        <h3>Aktualna tura: {{ data.current_move }}</h3>
        <div class="neutral-dice">
          <div class="neutral-block">
            <h4>Kości zapisane przeciwnika</h4>
            <DiceDisplay :dice="opponent.saved_dice" title="" />
          </div>

          <div class="neutral-block">
            <h4>Wybrany bóg przeciwnika</h4>
            <GodsDisplay
              v-if="opponent.chosen_god && opponent.chosen_god.name"
              :gods="[{ ...opponent.chosen_god, selected: true }]"
              :readonly="true"
            />
            <div v-if="opponent.chosen_god?.level">
              <h3>Poziom boga przeciwnika:{{ opponent.chosen_god.level }} </h3>
            </div>
          </div>

          <div class="neutral-block">
            <h4>Wybrany bóg</h4>
            <GodsDisplay
              v-if="player.chosen_god && player.chosen_god.name"
              :gods="[{ ...player.chosen_god, selected: true }]"
              :readonly="true"
            />
            <div v-if="player.chosen_god?.level">
              <h3>Wybrany poziom: {{ player.chosen_god.level }}</h3>
            </div>
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
              :selectable="isMyTurn"
              :selected-indexes="selectedDiceIndexes"
              @toggle-selection="toggleDieSelection"
            />
            <div v-if="isMyTurn" class="confirm-dice-wrapper">
              <button class="confirm-dice-button" @click="confirmDice">Zatwierdź</button>
            </div>
          </div>

          <GodsDisplay
            :gods="player.gods"
            :readonly="!isMyTurn"
            @choose-god="chooseGod"
          />
        </div>
      </div>

      <!-- Debug -->
      <div class="debug-controls">
        <button @click="toggleStage">Przełącz etap gry (DEBUG)</button>
      </div>
    </div>
  </div>
</template>

<script>
import PlayerStats from './PlayerStats.vue'
import DiceDisplay from './DiceDisplay.vue'
import GodsDisplay from './GodsDisplay.vue'

export default {
  components: { PlayerStats, DiceDisplay, GodsDisplay },
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
      return this.data.current_move === this.playerName
    },
    stage() {
      return this.data.stage
    }
  },
  methods: {
    submitName() {
      this.playerName = this.tempName
      this.loadMockData()
    },
    loadMockData() {
      this.data = {
        players: [
          {
            name: this.playerName,
            HP: 100,
            Mana: 3,
            rolled_dice: [
              { stat: 'helmet', gives_mana: false },
              { stat: 'mana', gives_mana: true },
              { stat: 'shield', gives_mana: false },
              { stat: 'mana', gives_mana: true },
              { stat: 'arrow', gives_mana: false },
              { stat: 'mana', gives_mana: false },
            ],
            saved_dice: [],
            gods: [
              { name: 'thor', description: 'Bóg piorunów', level: null },
              { name: 'loki', description: 'Bóg podziemi', level: null }
            ],
            chosen_god: null
          },
          {
            name: 'Bot',
            HP: 80,
            Mana: 5,
            rolled_dice: [
              { stat: 'axe', gives_mana: false }
            ],
            saved_dice: [
              { stat: 'helmet', gives_mana: false },
              { stat: 'mana', gives_mana: true },
              { stat: 'shield', gives_mana: false },
              { stat: 'mana', gives_mana: true },
              { stat: 'arrow', gives_mana: false },
              { stat: 'mana', gives_mana: false },
            ],
            gods: [
              { name: 'odin', description: 'Bóg wojny', level: null },
              { name: 'heimdall', description: 'Bóg słońca', level: null }
            ],
            chosen_god: null
          }
        ],
        current_move: this.playerName,
        winner: null,
        stage: 'gods'
      }
    },
    toggleDieSelection(index) {
      const pos = this.selectedDiceIndexes.indexOf(index)
      if (pos >= 0) this.selectedDiceIndexes.splice(pos, 1)
      else this.selectedDiceIndexes.push(index)
    },
    confirmDice() {
      const selectedDice = this.player.rolled_dice.filter((_, i) =>
        this.selectedDiceIndexes.includes(i)
      )
      this.player.saved_dice.push(...selectedDice)
      this.player.rolled_dice = this.player.rolled_dice.filter((_, i) =>
        !this.selectedDiceIndexes.includes(i)
      )
      this.selectedDiceIndexes = []
    },
    chooseGod({ godName, level }) {
      const god = this.player.gods.find(g => g.name === godName);
      if (god) {
        this.player.chosen_god = {
          ...god,
          level
        };
      }
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
  margin: 2rem 0;
  border: 1px solid #ccc;
  padding: 1rem;
  background: #f9f9f9;
  min-height: 450px;
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
