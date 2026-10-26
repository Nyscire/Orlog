<template>
  <div class="player-container" :class="{ 'my-turn': canSelectDice || canSelectGod }">
    <div class="player-header">
      <PlayerStats 
        :name="player.name" 
        :hp="player.HP"
        :mana="player.Mana"
        :pending-mana="pendingMana"
      />
      <div class="player-status">
        <span v-if="canSelectDice || canSelectGod" class="turn-badge">{{ $t('player.yourTurn') }}</span>
        <div class="rolls-counter" v-if="player.rzuty > 0" :title="$t('player.rollsTitle')">
          <span class="rolls-text">{{ $t('player.rollsLeft', { n: player.rzuty }) }}</span>
          <span class="pips">
            <span v-for="i in 3" :key="i" class="pip" :class="{ used: i > player.rzuty }"></span>
          </span>
        </div>
      </div>
    </div>

    <div class="player-content">
      <!-- Dice Section -->
      <div class="dice-section" v-if="player.rolled_dice?.length > 0 || canSelectDice">
        <div class="section-title">
          <h3>{{ canSelectDice ? $t('player.pickDice') : $t('player.yourDice') }}</h3>
          <div class="dice-counter" v-if="selectedDiceIndexes?.length > 0">
            {{ $t('player.selected', { n: selectedDiceIndexes.length }) }}
          </div>
        </div>
        
        <DiceDisplay
          :dice="player.rolled_dice || []"
          :selectable="canSelectDice"
          labels
          :selected-indexes="selectedDiceIndexes"
          @toggle-selection="$emit('toggle-die-selection', $event)"
        />
        
        <transition name="button-slide">
          <div v-if="canSelectDice" class="dice-actions">
            <button
              class="btn btn-gold confirm-dice-button"
              @click="$emit('confirm-dice')"
            >
              <span class="button-icon">✓</span>
              {{ confirmDiceLabel }}
            </button>
          </div>
        </transition>
      </div>

      <!-- Gods Section -->
      <div class="gods-section" v-if="player.gods?.length > 0">
        <div class="section-title">
          <h3>{{ canSelectGod ? $t('player.pickGod') : $t('player.yourGods') }}</h3>
          <div class="gods-status" v-if="player.chosen_god">
            {{ $t('player.chosen', { god: $t('gods.name', player.chosen_god) }) }}
          </div>
          <button v-if="canSelectGod" class="btn btn-ghost skip-god-button" @click="$emit('skip-god')">
            {{ $t('player.skipGod') }}
          </button>
        </div>
        
        <div class="gods-container">
          <GodsPlayerDisplay
            :gods="player.gods"
            :readonly="!canSelectGod"
            :chosen-god="player.chosen_god"
            :mana="player.mana_available ?? player.Mana ?? 0"
            :hp="player.HP ?? 0"
            :pick="pick"
            @choose-god="$emit('choose-god', $event)"
            @select-favor="$emit('select-favor', $event)"
            @amount="$emit('favor-amount', $event)"
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
    },
    // łaska wybierana w tej chwili (poziom, HP do poświęcenia, wskazane kości)
    pick: {
      type: Object,
      default: null
    }
  },
  computed: {
    pendingMana() {
      return Math.max((this.player.mana_available ?? 0) - (this.player.Mana ?? 0), 0)
    },
    confirmDiceLabel() {
      if (this.player.rzuty === 1) return this.$t('player.confirmLast')
      const count = this.selectedDiceIndexes?.length || 0
      return count > 0 ? this.$t('player.confirmSelected', { n: count }) : this.$t('player.rerollAll')
    }
  },
  emits: ['toggle-die-selection', 'confirm-dice', 'choose-god', 'skip-god', 'select-favor', 'favor-amount']
}
</script>

<style scoped>
.player-container {
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--panel-top) 0%, var(--parchment) 50%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 12px;
  box-shadow: 0 -2px 18px rgba(0, 0, 0, 0.35);
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

/* złota poświata, gdy gracz ma ruch */
.player-container.my-turn {
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.55), 0 0 22px rgba(var(--accent-rgb), 0.35);
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background: var(--glass);
  border-bottom: 1px solid var(--parchment-3);
  border-radius: 12px 12px 0 0;
}

.player-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.turn-badge {
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.8rem;
  color: var(--on-accent);
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
  border: 1px solid var(--gold-dark);
}

.rolls-counter {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.25rem 0.7rem;
  color: var(--ink-soft);
  background: var(--shade);
  border: 1px solid var(--parchment-3);
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.8rem;
}

.pips {
  display: flex;
  gap: 3px;
}

.pip {
  width: 9px;
  height: 9px;
  border-radius: 2px;
  background: var(--ink);
  transform: rotate(45deg);
}

.pip.used {
  background: transparent;
  border: 1px solid var(--edge);
  box-sizing: border-box;
}

.player-content {
  padding: 0.3rem 0.75rem 0.4rem;
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.dice-section,
.gods-section {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.dice-section {
  flex: 0 0 auto;
}

.gods-section {
  flex: 1;
  min-width: 0;
}

.section-title {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
}

.section-title h3 {
  margin: 0;
  font-family: var(--font-title);
  color: var(--ink);
  font-size: 1rem;
  font-weight: 700;
}

.dice-counter,
.gods-status {
  background: var(--parchment-3);
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--ink);
}

.dice-actions {
  display: flex;
  justify-content: center;
}

.confirm-dice-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.button-icon {
  font-size: 1rem;
  font-weight: 900;
}

.skip-god-button {
  padding: 0.25rem 0.9rem;
  font-size: 0.8rem;
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

/* węższe ekrany: kości nad bogami */
@media (max-width: 900px) {
  .player-content {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
}
</style>