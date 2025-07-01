<template>
  <div class="neutral-zone">
    <div class="stage-indicator">
      <div class="stage-badge" :class="stageClass">
        {{ stageText }}
      </div>
      <div class="turn-indicator" v-if="activePlayer">
        Tura: <span class="active-player">{{ activePlayer }}</span>
      </div>
    </div>

    <!-- Central Battle Area -->
    <div class="battle-arena">
      <div class="player-battle-side">
        <div class="saved-dice-area">
          <h4>Zapisane Kości</h4>
          <DiceDisplay
            :dice="player.saved_dice || []"
            :selectable="false"
          />
        </div>
        <div class="chosen-god-area" v-if="player.chosen_god">
          <GodsNeutralDisplay :god="player.chosen_god" />
        </div>
      </div>

      <div class="vs-divider">
        <div class="vs-circle">VS</div>
      </div>

      <div class="opponent-battle-side">
        <div class="saved-dice-area">
          <h4>Zapisane Kości Przeciwnika</h4>
          <DiceDisplay
            :dice="opponent.saved_dice || []"
            :selectable="false"
          />
        </div>
        <div class="chosen-god-area" v-if="opponent.chosen_god">
          <GodsNeutralDisplay :god="opponent.chosen_god" />
        </div>
      </div>
    </div>

    <!-- Stage Instructions -->
    <div class="instructions">
      <div v-if="stage === 'dice'" class="instruction-text">
        <span v-if="activePlayer === player.name">
          Wybierz kości do zachowania i kliknij "Zatwierdź"
        </span>
        <span v-else>
          {{ activePlayer }} wybiera kości...
        </span>
      </div>
      <div v-else-if="stage === 'gods'" class="instruction-text">
        <span v-if="activePlayer === player.name">
          Wybierz boga i jego poziom
        </span>
        <span v-else>
          {{ activePlayer }} wybiera boga...
        </span>
      </div>
      <div v-else-if="stage === 'battle'" class="instruction-text">
        Walka w toku! Sprawdź wyniki...
      </div>
    </div>
  </div>
</template>

<script>
import DiceDisplay from './DiceDisplay.vue'
import GodsNeutralDisplay from './GodsNeutralDisplay.vue'

export default {
  name: 'NeutralZone',
  components: {
    DiceDisplay,
    GodsNeutralDisplay
  },
  props: {
    stage: {
      type: String,
      default: 'waiting'
    },
    activePlayer: String,
    player: {
      type: Object,
      default: () => ({})
    },
    opponent: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    stageText() {
      const stages = {
        'waiting': 'Oczekiwanie na graczy',
        'dice': 'Faza Kości',
        'gods': 'Wybór Bogów',
        'battle': 'Walka!',
        'finished': 'Koniec Gry'
      }
      return stages[this.stage] || 'Nieznana faza'
    },
    stageClass() {
      return {
        'stage-waiting': this.stage === 'waiting',
        'stage-dice': this.stage === 'dice',
        'stage-gods': this.stage === 'gods',
        'stage-battle': this.stage === 'battle',
        'stage-finished': this.stage === 'finished'
      }
    }
  }
}
</script>

<style scoped>
.neutral-zone {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1rem;
  background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
  border-radius: 12px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stage-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stage-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stage-waiting {
  background: linear-gradient(135deg, #9e9e9e, #757575);
  color: white;
}

.stage-dice {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  color: white;
}

.stage-gods {
  background: linear-gradient(135deg, #9c27b0, #7b1fa2);
  color: white;
}

.stage-battle {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  animation: battlePulse 2s ease-in-out infinite;
}

.stage-finished {
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
}

@keyframes battlePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.turn-indicator {
  font-size: 0.9rem;
  color: #5d4037;
}

.active-player {
  font-weight: bold;
  color: #d32f2f;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.battle-arena {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  margin: 1rem 0;
}

.player-battle-side,
.opponent-battle-side {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.saved-dice-area {
  background: rgba(255, 255, 255, 0.8);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 300px;
}

.saved-dice-area h4 {
  margin: 0 0 0.5rem 0;
  text-align: center;
  color: #3e2723;
  font-size: 0.9rem;
}

.chosen-god-area {
  background: rgba(255, 255, 255, 0.9);
  padding: 0.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.vs-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 80px;
}

.vs-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff5722, #d84315);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: vsRotate 4s linear infinite;
}

@keyframes vsRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.instructions {
  background: rgba(255, 255, 255, 0.9);
  padding: 0.75rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
}

.instruction-text {
  font-size: 0.9rem;
  color: #3e2723;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-height: 700px) {
  .neutral-zone {
    padding: 0.5rem;
  }
  
  .battle-arena {
    gap: 1rem;
    margin: 0.5rem 0;
  }
  
  .saved-dice-area {
    padding: 0.75rem;
  }
  
  .vs-circle {
    width: 50px;
    height: 50px;
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .battle-arena {
    flex-direction: column;
    gap: 1rem;
  }
  
  .vs-divider {
    transform: rotate(90deg);
  }
  
  .stage-indicator {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>