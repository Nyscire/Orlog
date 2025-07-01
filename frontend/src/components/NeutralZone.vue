<template>
  <div class="player-container">
    <div class="player-content">
      <div class="stats-section">
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
        
        <div class="rolls-info">
          <h4>Rzuty: {{ player.rzuty }}</h4>
        </div>
      </div>

      <div class="gods-section">
        <GodsPlayerDisplay
          :gods="player.gods"
          :readonly="!canSelectGod"
          @choose-god="$emit('choose-god', $event)"
        />
      </div>
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
.player-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.player-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  height: 100%;
  max-height: 180px;
}

.stats-section {
  flex: 0 0 200px;
  display: flex;
  justify-content: center;
}

.dice-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  max-width: 300px;
}

.gods-section {
  flex: 2;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

.confirm-dice-wrapper {
  text-align: center;
}

.confirm-dice-button {
  padding: 0.4rem 0.8rem;
  font-weight: 600;
  cursor: pointer;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.confirm-dice-button:hover {
  background-color: #218838;
}

.rolls-info h4 {
  margin: 0;
  font-size: 0.9rem;
  text-align: center;
}

/* Button fade animation */
.button-fade-enter-active {
  transition: all 0.3s ease;
}
.button-fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

/* Compact layout adjustments */
@media (max-height: 800px) {
  .player-content {
    max-height: 160px;
  }
}

@media (max-height: 700px) {
  .player-content {
    max-height: 140px;
    gap: 0.5rem;
  }
  
  .stats-section {
    flex: 0 0 180px;
  }
  
  .dice-section {
    gap: 0.25rem;
  }
}
</style>