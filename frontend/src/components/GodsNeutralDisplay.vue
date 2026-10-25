<template>
  <div class="god-card neutral-god-card">
    <h4 class="god-name">{{ god.name }}</h4>
    <img :src="`/img/icons/${god.name.toLowerCase()}.png`" alt="" class="god-icon" />
    <div class="god-level" v-if="god.level">Poziom {{ god.level }}</div>

    <!-- Tooltip – wyświetlany przy hover -->
    <div class="tooltip-card" :class="`tooltip-${tooltipAlign}`">
      {{ god.level ? god.levels?.[god.level-1] : god.description }}
    </div>
  </div>
</template>

<script>
export default {
  name: "GodsNeutralDisplay",
  props: {
    god: {
      type: Object,
      required: true
    },
    // do której krawędzi karty przyklejony jest tooltip, żeby nie wychodził poza ekran
    tooltipAlign: {
      type: String,
      default: 'center'
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
  background: #fff4d6;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.god-icon {
  width: 32px;
  height: 32px;
  margin-top: 0.25rem;
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
  white-space: pre-wrap;
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
</style>
