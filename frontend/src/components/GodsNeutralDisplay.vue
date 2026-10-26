<template>
  <div class="god-card neutral-god-card">
    <h4 class="god-name">{{ $t('gods.name', god) }}</h4>
    <img :src="icon" alt="" class="god-icon" />
    <div class="god-level" v-if="god.level">{{ $t('gods.level', { level: god.level }) }}</div>

    <!-- opis wybranej łaski, przy najechaniu -->
    <div class="tooltip-card" :class="`tooltip-${tooltipAlign}`">
      <div class="tooltip-title">{{ $t('gods.favor', god) }}</div>
      <div>{{ god.level ? $t('gods.levelEffect', { god: god, level: god.level }) : $t('gods.describe', god) }}</div>
      <div v-if="choice && choice.amount" class="tooltip-extra">{{ $t('gods.sacrificed', { n: choice.amount }) }}</div>
    </div>
  </div>
</template>

<script>
import { godIcon } from '../dice'

export default {
  name: "GodsNeutralDisplay",
  props: {
    god: {
      type: Object,
      required: true
    },
    // dodatkowy wybór gracza (np. ile HP poświęca Odyn)
    choice: {
      type: Object,
      default: null
    },
    // do której krawędzi karty przyklejony jest tooltip, żeby nie wychodził poza ekran
    tooltipAlign: {
      type: String,
      default: 'center'
    }
  },
  computed: {
    icon() {
      return godIcon(this.god.name)
    }
  }
}
</script>

<style scoped>
.god-card {
  position: relative;
  overflow: visible;
  border: 1.5px solid var(--gold);
  border-radius: 0.5rem;
  padding: 0.4rem 0.5rem;
  box-sizing: border-box;
  width: 110px;
  color: var(--ink);
  background: var(--card-hi);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.god-icon {
  width: 32px;
  height: 32px;
  margin-top: 0.25rem;
  filter: var(--icon-filter);
}

.god-name {
  margin: 0;
  font-family: var(--font-title);
  font-size: 0.95rem;
}

.god-level {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--gold-dark);
}

.tooltip-card {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 180px;
  color: var(--ink);
  background: var(--parchment);
  border: 1px solid var(--edge);
  border-radius: 6px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  padding: 8px;
  margin-top: 8px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
  z-index: 20;
  animation: none;
}

.tooltip-card.tooltip-left {
  left: 0;
  transform: none;
}

.tooltip-card.tooltip-right {
  left: auto;
  right: 0;
  transform: none;
}

.god-card:hover .tooltip-card {
  opacity: 1;
}

.tooltip-title {
  font-family: var(--font-title);
  font-weight: 700;
}

.tooltip-extra {
  margin-top: 0.2rem;
  font-weight: 700;
}
</style>
