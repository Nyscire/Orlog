<template>
  <div class="player-container">
    <div class="player-header">
      <PlayerStats 
        :name="player.name" 
        :hp="player.HP" 
        :mana="player.Mana" 
      />
      <div class="player-status" v-if="player.rzuty !== undefined">
        <div class="rolls-counter">
          <span class="rolls-icon">🎲</span>
          <span class="rolls-text">Rzuty: {{ player.rzuty }}/3</span>
        </div>
      </div>
    </div>

    <div class="player-content">
      <!-- Dice Section -->
      <div class="dice-section" v-if="player.rolled_dice?.length > 0 || canSelectDice">
        <div class="section-title">
          <h3>{{ canSelectDice ? 'Wybierz Kości' : 'Twoje Kości' }}</h3>
          <div class="dice-counter" v-if="selectedDiceIndexes?.length > 0">
            Wybrano: {{ selectedDiceIndexes.length }}
          </div>
        </div>
        
        <DiceDisplay
          :dice="player.rolled_dice || []"
          :selectable="canSelectDice"
          :selected-indexes="selectedDiceIndexes"
          @toggle-selection="$emit('toggle-die-selection', $event)"
        />
        
        <transition name="button-slide">
          <div v-if="canSelectDice && selectedDiceIndexes?.length > 0" class="dice-actions">
            <button 
              class="confirm-dice-button" 
              @click="$emit('confirm-dice')"
            >
              <span class="button-icon">✓</span>
              Zatwierdź Wybrane ({{ selectedDiceIndexes.length }})
            </button>
          </div>
        </transition>
      </div>

      <!-- Gods Section -->
      <div class="gods-section" v-if="player.gods?.length > 0">
        <div class="section-title">
          <h3>{{ canSelectGod ? 'Wybierz Boga' : 'Twoi Bogowie' }}</h3>
          <div class="gods-status" v-if="player.chosen_god">
            Wybrany: {{ player.chosen_god.name }}
          </div>
        </div>
        
        <div class="gods-container">
          <GodsPlayerDisplay
            :gods="player.gods"
            :readonly="!canSelectGod"
            :chosen-god="player.chosen_god"
            @choose-god="$emit('choose-god', $event)"
          />
        </div>
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
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  border-radius: 12px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 2px solid #a5d6a7;
  backdrop-filter: blur(10px);
}

.player-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.rolls-counter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.85rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.rolls-icon {
  font-size: 1rem;
}

.player-content {
  flex: 1;
  padding: 1rem;
  display: flex;
  gap: 1.5rem;
  overflow: hidden;
}

.dice-section,
.gods-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dice-section {
  flex: 0 0 300px;
  max-width: 350px;
}

.gods-section {
  flex: 1;
  min-width: 0;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.section-title h3 {
  margin: 0;
  color: #2e7d32;
  font-size: 1.1rem;
  font-weight: 600;
}

.dice-counter,
.gods-status {
  background: rgba(76, 175, 80, 0.2);
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #1b5e20;
}

.dice-actions {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.confirm-dice-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  cursor: pointer;
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
  border: none;
  border-radius: 25px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  font-size: 0.9rem;
}

.confirm-dice-button:hover {
  background: linear-gradient(135deg, #66bb6a, #4caf50);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.confirm-dice-button:active {
  transform: translateY(0);
}

.button-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.gods-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Animations */
.button-slide-enter-active {
  transition: all 0.4s ease;
}

.button-slide-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

.button-slide-leave-active {
  transition: all 0.3s ease;
}

.button-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Responsive adjustments */
@media (max-height: 800px) {
  .player-header {
    padding: 0.75rem;
  }
  
  .player-content {
    padding: 0.75rem;
    gap: 1rem;
  }
  
  .dice-section {
    flex: 0 0 250px;
  }
}

@media (max-height: 700px) {
  .player-header {
    padding: 0.5rem;
  }
  
  .player-content {
    padding: 0.5rem;
    gap: 0.75rem;
  }
  
  .section-title h3 {
    font-size: 1rem;
  }
}

@media (max-width: 1024px) {
  .player-content {
    flex-direction: column;
  }
  
  .dice-section {
    flex: none;
    max-width: none;
  }
  
  .gods-section {
    flex: none;
  }
  
  .gods-container {
    max-height: 200px;
  }
}
</style>