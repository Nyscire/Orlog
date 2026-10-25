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
          :dice="opponent.rolled_dice || []"
          :title="$t('opponent.roll')"
          :selectable="false"
          compact
          tooltip-placement="below"
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
.opponent-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
}

.stats-section {
  flex: 0 0 auto;
}

.dice-section {
  flex: 0 1 auto;
  display: flex;
  justify-content: center;
}

.gods-section {
  flex: 1 1 auto;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .opponent-content {
    justify-content: center;
  }

  .gods-section {
    justify-content: center;
  }
}
</style>