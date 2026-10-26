<template>
  <div class="gods-display">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card"
      :class="{ selected: isSelected(god), compact: readonly, picking: levelOf(god) != null }"
    >
      <img :src="icon(god)" alt="" class="god-icon" />
      <h3 class="god-name">{{ $t('gods.name', god) }}</h3>

      <div class="level-buttons" v-if="!readonly">
        <button
          v-for="level in [1, 2, 3]"
          :key="level"
          :class="{ active: levelOf(god) === level }"
          :disabled="!canAfford(god, level)"
          :title="levelLabel(god, level)"
          @click="selectLevel(god, level)"
          class="level-btn"
        >
          {{ level }}
        </button>
        <button
          class="confirm-btn"
          :disabled="!canConfirm(god)"
          @click="confirmGod(god)"
        >
          {{ $t('gods.choose') }}
        </button>
      </div>

      <!-- bez wybranego poziomu: co robi łaska; z poziomem: efekt i koszt tego poziomu -->
      <div class="level-description" v-if="!readonly">
        {{ levelOf(god) ? levelLabel(god, levelOf(god)) : $t('gods.describe', god) }}
      </div>

      <!-- Odyn i Tyr: ile HP poświęcić -->
      <div v-if="!readonly && levelOf(god) && god.needs === 'amount'" class="choice stepper">
        <span class="choice-label">{{ $t('gods.sacrifice') }}</span>
        <button class="step-btn" :aria-label="$t('gods.less')" :disabled="amount <= 1" @click="setAmount(amount - 1)">−</button>
        <strong class="amount-value">{{ amount }} HP</strong>
        <button class="step-btn" :aria-label="$t('gods.more')" :disabled="amount >= maxAmount" @click="setAmount(amount + 1)">+</button>
        <span class="choice-result">{{ $t('gods.sacrificeResult', { god: god, level: levelOf(god), amount: amount }) }}</span>
      </div>

      <!-- Frigg i Loki: kości wskazuje się na stole -->
      <div v-if="!readonly && levelOf(god) && isDiceFavor(god)" class="choice targets" :class="{ done: picked > 0 }">
        {{ $t('gods.pickTargets', { picked: picked, max: god.values[levelOf(god) - 1] }) }}
      </div>

      <!-- ogólny opis łaski -->
      <div class="tooltip-card">
        <div class="tooltip-title">{{ $t('gods.favor', god) }}</div>
        <div class="tooltip-phase">{{ $t('gods.phase.' + god.phase) }}</div>
        <div>{{ $t('gods.describe', god) }}</div>
        <div class="tooltip-costs">{{ $t('gods.costs', god) }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { godIcon } from '../dice'

export default {
  props: {
    gods: Array,
    readonly: Boolean,
    chosenGod: Object,
    // Mana dostępna w chwili aktywacji łaski
    mana: {
      type: Number,
      default: 0
    },
    hp: {
      type: Number,
      default: 21
    },
    // wybór w toku: { name, level, needs, amount, own, opponent } (trzyma go GameBoard)
    pick: {
      type: Object,
      default: null
    }
  },
  emits: ['choose-god', 'select-favor', 'amount'],
  computed: {
    amount() {
      return this.pick?.amount || 1
    },
    maxAmount() {
      return Math.max((this.hp || 0) - 1, 1)
    },
    picked() {
      return (this.pick?.own?.length || 0) + (this.pick?.opponent?.length || 0)
    }
  },
  methods: {
    icon(god) {
      return godIcon(god.name)
    },
    levelOf(god) {
      return this.pick && this.pick.name === god.name ? this.pick.level : null
    },
    cost(god, level) {
      return god.mana_costs?.[level - 1] ?? 0
    },
    canAfford(god, level) {
      return this.cost(god, level) <= this.mana
    },
    isDiceFavor(god) {
      return god.needs === 'opponent_dice' || god.needs === 'any_dice'
    },
    canConfirm(god) {
      if (this.levelOf(god) == null) return false
      if (this.isDiceFavor(god)) return this.picked > 0
      if (god.needs === 'amount') return this.hp > 1
      return true
    },
    // "Poziom 2: 5 obrażeń (8 many)"
    levelLabel(god, level) {
      return this.$t('gods.levelText', { level, text: this.$t('gods.levelEffect', { god, level }) })
    },
    selectLevel(god, level) {
      this.$emit('select-favor', { god, level })
    },
    setAmount(value) {
      this.$emit('amount', value)
    },
    confirmGod(god) {
      this.$emit('choose-god', { godName: god.name, level: this.levelOf(god) })
    },
    isSelected(god) {
      return this.chosenGod && this.chosenGod.name === god.name
    }
  }
}
</script>

<style scoped>
.gods-display {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding: 0.25rem 0;
}

/* pionowa karta jak u przeciwnika: ikona, pod nią nazwa */
.god-card {
  border: 1.5px solid var(--edge);
  border-radius: 10px;
  padding: 0.4rem 0.5rem 0.4rem;
  width: 240px;
  box-sizing: border-box;
  background: var(--parchment);
  position: relative;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* poza fazą bogów: taka sama karta jak bogowie przeciwnika */
.god-card.compact {
  width: 110px;
  padding: 6px 8px;
  gap: 2px;
}

.god-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.god-card.selected {
  border-color: var(--gold);
  background: var(--card-hi);
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.45);
}

.god-name {
  margin: 0;
  font-family: var(--font-title);
  font-size: 0.95rem;
  color: var(--ink);
}

.compact .god-name {
  font-size: 14px;
}

.god-icon {
  width: 30px;
  height: 30px;
  filter: var(--icon-filter);
}

.compact .god-icon {
  width: 32px;
  height: 32px;
}

.level-buttons {
  display: flex;
  gap: 0.25rem;
  align-items: center;
  justify-content: center;
}

.level-btn {
  padding: 0.2rem 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  color: var(--ink);
  border-radius: 4px;
  border: 1px solid var(--edge);
  background-color: var(--input-bg);
  transition: all 0.2s ease;
  min-width: 24px;
}

.level-btn:hover:not(:disabled) {
  background-color: var(--parchment-2);
}

.level-btn.active {
  background-color: var(--ink);
  color: var(--parchment);
  border-color: var(--ink);
}

.level-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.confirm-btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  font-weight: bold;
  color: var(--on-accent);
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
  border: 1px solid var(--gold-dark);
  border-radius: 4px;
  cursor: pointer;
}

.confirm-btn:disabled {
  color: var(--ink-soft);
  background: var(--parchment-3);
  border-color: var(--parchment-3);
  cursor: not-allowed;
}

.level-description {
  font-size: 0.75rem;
  text-align: center;
  line-height: 1.2;
}

/* dodatkowy wybór łaski (HP do poświęcenia, kości na stole) */
.choice {
  width: 100%;
  box-sizing: border-box;
  padding: 0.15rem 0.35rem;
  font-size: 0.72rem;
  line-height: 1.25;
  text-align: center;
  color: var(--ink);
  background: var(--glass);
  border: 1px dashed var(--edge);
  border-radius: 6px;
}

.choice.targets {
  font-weight: 700;
  border-color: var(--gold);
  animation: targetPulse 1.6s ease-in-out infinite;
}

.choice.targets.done {
  animation: none;
  border-style: solid;
}

@keyframes targetPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0); }
  50% { box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.35); }
}

.stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.15rem 0.3rem;
}

.choice-label {
  font-weight: 700;
  margin-right: 0.15rem;
}

.step-btn {
  width: 22px;
  height: 22px;
  padding: 0;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 900;
  line-height: 1;
  color: var(--ink);
  background: var(--input-bg);
  border: 1px solid var(--edge);
  border-radius: 4px;
  cursor: pointer;
}

.step-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.amount-value {
  min-width: 2.6rem;
  font-size: 0.85rem;
}

.choice-result {
  margin-left: 0.15rem;
  color: var(--mana);
  font-weight: 700;
}

/* ogólny opis boga, widoczny po najechaniu na kartę */
.tooltip-card {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 210px;
  margin-bottom: 6px;
  padding: 8px;
  color: var(--ink);
  background: var(--parchment);
  border: 1px solid var(--edge);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  font-size: 13px;
  z-index: 20;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
  animation: none;
}

.god-card:hover .tooltip-card {
  opacity: 1;
}

.tooltip-title {
  font-family: var(--font-title);
  font-weight: 700;
}

.tooltip-phase {
  margin-bottom: 0.2rem;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--ink-soft);
}

.tooltip-costs {
  margin-top: 0.25rem;
  font-size: 12px;
  color: var(--ink-soft);
}
</style>