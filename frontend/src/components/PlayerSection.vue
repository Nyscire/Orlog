<template>
  <div class="player-section self compact-layout">
    <div class="horizontal-group">
      <div class="actions-and-stats">
        <PlayerStats 
          :name="player.name" 
          :hp="player.HP" 
          :mana="player.Mana" 
        />
      </div>
      
      <div class="dice-section">
        <DiceDisplay
          :dice="player.rolled_dice"
          title="Wylosowane Kości"
          :selectable="canSelectDice"
          :selected-indexes="selectedDiceIndexes"
          @toggle-selection="$emit('toggle-die-selection', $event)"
        />
        
        <transition name="button-fade">
          <div v-if="canSelectDice" class="confirm-dice-wrapper">
            <button 
              class="confirm-dice-button" 
              @click="$emit('confirm-dice')"
            >
              Zatwierdź
            </button>
          </div>
        </transition>
        
        <div>
          <h4>Ilość rzutów: {{ player.rzuty }}</h4>
        </div>
      </div>

      <GodsPlayerDisplay
        :gods="player.gods"
        :readonly="!canSelectGod"
        @choose-god="$emit('choose-god', $event)"
      />
    </div>
  </div>
</template>

<script>
import PlayerStats from './PlayerStats.vue'
import DiceDisplay from './DiceDisplay.vue'
import GodsPlayerDisplay from './GodsPlayerDisplay.vue'

export default {
  name: 'PlayerSection',
  components: {
    PlayerStats,
    DiceDisplay,
    GodsPlayerDisplay
  },
  props: {
    player: {
      type: Object,
      default: () => ({})
    },
    canSelectDice: {
      type: Boolean,
      default: false
    },
    canSelectGod: {
      type: Boolean,
      default: false
    },
    selectedDiceIndexes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['toggle-die-selection', 'confirm-dice', 'choose-god']
}
</script>

<style scoped>
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

.confirm-dice-wrapper {
  margin-top: 0.5rem;
  text-align: center;
}

.confirm-dice-button {
  padding: 0.5rem 1rem;
  font-weight: 600;
  cursor: pointer;
}

h3, h4 {
  text-align: center;
}

/* For buttons that become available */
.button-fade-enter-active {
  transition: all 0.3s ease;
}
.button-fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}
</style>