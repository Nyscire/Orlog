<template>
  <div class="player-section opponent compact-layout">
    <div class="horizontal-group">
      <div class="actions-and-stats">
        <PlayerStats 
          :name="opponent.name" 
          :hp="opponent.HP" 
          :mana="opponent.Mana" 
        />
      </div>
      
      <DiceDisplay
        :dice="opponent.rolled_dice"
        title="Kości przeciwnika"
        :selectable="false"
      />
      
      <GodsOpponentDisplay
        :gods="opponent.gods"
        :readonly="true" 
      />
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
</style>