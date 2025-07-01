<template>
  <div class="opponent-container">
    <div class="opponent-content">
      <div class="stats-section">
        <PlayerStats 
          :name="opponent.name" 
          :hp="opponent.HP" 
          :mana="opponent.Mana" 
        />
      </div>
      
      <div class="dice-section">
        <DiceDisplay
          :dice="opponent.rolled_dice"
          title="Kości przeciwnika"
          :selectable="false"
        />
      </div>
      
      <div class="gods-section">
        <GodsOpponentDisplay
          :gods="opponent.gods"
          :readonly="true" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import PlayerStats from './PlayerStats.vue'
import DiceDisplay from './DiceDisplay.vue'
import GodsOpponentDisplay from './GodsOpponentDisplay.vue'

export default {
  name: 'OpponentSection',
  components: {
    PlayerStats,
    DiceDisplay,
    GodsOpponentDisplay
  },
  props: {
    opponent: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.opponent-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.opponent-content {
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
  justify-content: center;
  max-width: 300px;
}

.gods-section {
  flex: 2;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

/* Compact layout adjustments */
@media (max-height: 800px) {
  .opponent-content {
    max-height: 160px;
  }
}

@media (max-height: 700px) {
  .opponent-content {
    max-height: 140px;
    gap: 0.5rem;
  }
  
  .stats-section {
    flex: 0 0 180px;
  }
}
</style>