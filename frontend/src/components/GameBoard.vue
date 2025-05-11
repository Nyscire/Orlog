<template>
  <div class="game-container">
    <div v-if="!playerName" class="name-entry">
      <input v-model="tempName" placeholder="Podaj swoją nazwę" />
      <button @click="submitName">Zatwierdź</button>
    </div>

    <div v-else class="game-interface">
      <!-- Oponent -->
      <div class="player-section opponent compact-layout">
        <div class="dice-and-gods">
          <PlayerStats :name="opponent.name" :hp="opponent.HP" :mana="opponent.Mana" :gods="opponent.gods" />
          <GodsDisplay :gods="opponent.gods" :readonly="true" />
        </div>
        <div class="actions-and-stats">
          <DiceDisplay :dice="opponent.rolled_dice" title="Kości przeciwnika" />
        </div>
      </div>

      <!-- Strefa neutralna -->
      <div class="neutral-section">
        <h3>Aktualna tura: {{ data.current_move }}</h3>

        <div class="neutral-dice">
          <div>
            <h4>Kości zapisane przeciwnika</h4>
            <DiceDisplay :dice="opponent.saved_dice" title="" />
          </div>

          <div>
            <h4>Wybrany bóg przeciwnika</h4>
            <GodsDisplay :gods="[opponent.chosen_god]" :readonly="true" />
          </div>

          <div>
            <h4>Kości zapisane gracza</h4>
            <DiceDisplay :dice="player.saved_dice" title="" />
          </div>

          <div>
            <h4>Wybrany bóg</h4>
            <GodsDisplay :gods="[player.chosen_god]" :readonly="true" />
          </div>
        </div>
      </div>

      <!-- Gracz -->
      <div class="player-section self compact-layout">
        <div class="dice-and-gods">
          <DiceDisplay
            :dice="player.rolled_dice"
            title="Wylosowane Kości"
            :selectable="isMyTurn"
            @toggle-selection="toggleDieSelection"
          />
          <GodsDisplay
            :gods="player.gods"
            :readonly="!isMyTurn"
            @choose-god="chooseGod"
          />
        </div>

        <div class="actions-and-stats">
          <div v-if="isMyTurn">
            <button @click="confirmDice">Zatwierdź</button>
          </div>
          <PlayerStats :name="player.name" :hp="player.HP" :mana="player.Mana" :gods="player.gods" />
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
import GodsList from './GodsList.vue'

export default {
  components: { PlayerStats, DiceDisplay, GodsDisplay, GodsList },
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
              { stat: 'mana', gives_mana: true }
            ],
            saved_dice: [],
            gods: [
              { name: 'thor', description: 'Bóg piorunów' },
              { name: 'loki', description: 'Bóg podziemi' }
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
            saved_dice: [],
            gods: [
              { name: 'odin', description: 'Bóg wojny' },
              { name: 'heimdall', description: 'Bóg słońca' }
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
    chooseGod(godName) {
      this.player.chosen_god = this.player.gods.find(g => g.name === godName)
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
  margin: 2rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.compact-layout {
  flex-direction: row;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 1rem;
}
.dice-and-gods {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.actions-and-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.opponent {
  border-bottom: 2px dashed #ccc;
  padding-bottom: 1rem;
}
.self {
  border-top: 2px dashed #ccc;
  padding-top: 1rem;
}
.neutral-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2rem 0;
}
.neutral-dice {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 1rem;
}
</style>
