<template>
  <div class="gods-display">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card"
      :class="{ selected: isSelected(god), compact: readonly }"
    >
      <img :src="`/img/icons/${god.name.toLowerCase()}.png`" alt="" class="god-icon" />
      <h3 class="god-name">{{ god.name }}</h3>

      <div class="level-buttons" v-if="!readonly">
        <button
          v-for="level in [1, 2, 3]"
          :key="level"
          :class="{ active: god.level === level }"
          :disabled="!canAfford(god, level)"
          :title="costLabel(god, level)"
          @click="selectLevel(god.name, level)"
          class="level-btn"
        >
          {{ level }}
        </button>
        <button
          class="confirm-btn"
          :disabled="god.level == null"
          @click="confirmGod(god)"
        >
          Wybierz
        </button>
      </div>

      <!-- bez wybranego poziomu: co robi bóg; z poziomem: efekt i koszt tego poziomu -->
      <div class="level-description" v-if="!readonly">
        {{ god.level ? `Poziom ${god.level}: ${god.levels[god.level - 1]}` : effect(god) }}
      </div>

      <!-- Tooltip: OGÓLNY opis boga -->
      <div class="tooltip-card">
        {{ god.description }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    gods: Array,
    readonly: Boolean,
    chosenGod: Object,
    // Mana dostępna w chwili aktywacji łaski (zebrana + z zachowanych kości)
    mana: {
      type: Number,
      default: 0
    }
  },
  methods: {
    cost(god, level) {
      return god.mana_costs?.[level - 1] ?? 0;
    },
    canAfford(god, level) {
      return this.cost(god, level) <= this.mana;
    },
    costLabel(god, level) {
      return `Poziom ${level}: ${god.levels?.[level - 1] || ''}`;
    },
    effect(god) {
      return (god.description || '').split('\n').filter(line => !line.startsWith('Koszt')).join(' ');
    },
    selectLevel(godName, level) {
      this.gods.forEach(god => {
        god.level = god.name === godName ? level : null;
      });
    },
    confirmGod(god) {
      this.$emit('choose-god', { godName: god.name, level: god.level });
    },
    isSelected(god) {
      return this.chosenGod && this.chosenGod.name === god.name;
    }
  }
};
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
  padding: 0.45rem 0.5rem 0.5rem;
  width: 195px;
  box-sizing: border-box;
  background: var(--parchment);
  position: relative;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
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
  background: #fff4d6;
  box-shadow: 0 0 0 2px rgba(201, 162, 76, 0.45);
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
  width: 34px;
  height: 34px;
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
  background-color: #fffaf0;
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
  color: var(--wood-900);
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

/* ogólny opis boga, widoczny po najechaniu na kartę */
.tooltip-card {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 180px;
  margin-bottom: 6px;
  padding: 8px;
  color: var(--ink);
  background: var(--parchment);
  border: 1px solid var(--edge);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  font-size: 13px;
  white-space: pre-wrap;
  z-index: 20;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
  animation: none;
}

.god-card:hover .tooltip-card {
  opacity: 1;
}
</style>