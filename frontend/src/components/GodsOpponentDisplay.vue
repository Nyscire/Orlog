<template>
  <div class="gods-container">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card disabled"
    >
      <img :src="icon(god)" alt="" class="god-icon" />
      <h3 class="god-name">{{ $t('gods.name', god) }}</h3>

      <div class="chosen-level" v-if="god.level">
        <strong>{{ $t('gods.level', { level: god.level }) }}</strong>
      </div>

      <!-- opis łaski, widoczny przy najechaniu -->
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
  props: { gods: Array },
  methods: {
    icon(god) {
      return godIcon(god.name)
    }
  }
};
</script>

<style scoped>
@import "@/assets/GodCardStyles.css";

/* upewnij się, że karta jest punktem odniesienia */
.god-card {
  position: relative;
  overflow: visible;     /* pozwól tooltipowi wychodzić poza kartę */
}

/* Tooltip – domyślnie ukryty i absolutnie pozycjonowany */
.tooltip-card {
  position: absolute;
  top: 100%;             /* tuż pod kartą */
  right: 0;              /* karty są przy prawej krawędzi, więc tooltip nie wychodzi poza ekran */
  width: 180px;          /* stała szerokość jak w innych tooltipach */
  color: var(--ink);
  background: var(--parchment);
  border: 1px solid var(--edge);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,.3);
  font-size: 13px;
  padding: 8px;
  margin-top: 8px;       /* niewielki odstęp od karty */
  opacity: 0;
  pointer-events: none;
  transition: opacity .25s ease;
  z-index: 20;
  animation: none;
}

/* pokazuj tooltip tylko przy najechaniu na całą kartę */
.god-card:hover .tooltip-card {
  opacity: 1;
}

.god-icon {
  filter: var(--icon-filter);
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
