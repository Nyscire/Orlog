<template>
  <div class="neutral-section">
    <transition name="fade" mode="out-in">
      <div v-if="stage === 'dice'">
        <h3>Aktualny etap: Wybór kości</h3>
      </div>
      <div v-else>
        <h3>Aktualny etap: Wybór boga</h3>
      </div>
    </transition>
    
    <h3>Aktualna tura: {{ activePlayer }}</h3>

    <div class="neutral-dice">
      <div class="neutral-block">
        <h4>Kości zapisane przeciwnika</h4>
        <DiceDisplay :dice="opponent.saved_dice" title="" />
      </div>

      <div class="neutral-block">
        <h4>Wybrany bóg przeciwnika</h4>
        <GodsNeutralDisplay
          v-if="opponent.chosen_god && opponent.chosen_god.name"
          :god="opponent.chosen_god"
        />
      </div>

      <div class="neutral-block">
        <h4>Wybrany bóg</h4>
        <transition name="god-fade">
          <GodsNeutralDisplay
            v-if="player.chosen_god && player.chosen_god.name"
            :god="player.chosen_god"
          />
        </transition>
      </div>

      <div class="neutral-block">
        <h4>Kości zapisane gracza</h4>
        <DiceDisplay :dice="player.saved_dice" title="" />
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
      default: 'dice'
    },
    activePlayer: {
      type: String,
      default: ''
    },
    opponent: {
      type: Object,
      default: () => ({})
    },
    player: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.neutral-section {
  border: 1px solid #ccc;
  height: 361px;
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
  max-width: 220px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h3, h4 {
  text-align: center;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* For god cards */
.god-fade-enter-active, .god-fade-leave-active {
  transition: opacity 0.5s ease;
}
.god-fade-enter-from, .god-fade-leave-to {
  opacity: 0;
}
</style>