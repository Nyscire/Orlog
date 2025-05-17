<template>
  <div class="gods-container">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card disabled"
    >
      <img :src="`/img/icons/${god.name}.png`" alt="Ikona boga" class="god-icon" />
      <h3 class="god-name">{{ god.name }}</h3>

      <div class="chosen-level" v-if="god.level">
        <strong>Poziom: {{ god.level }}</strong>
      </div>

      <!-- Tooltip – zawsze w DOM, ale widoczny tylko przy hover -->
      <div
        class="tooltip-card"
      >
        {{ god.level ? god.levels?.[god.level] : god.description }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: { gods: Array }
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
  left: 50%;
  transform: translateX(-50%);
  width: 180px;          /* stała szerokość jak w innych tooltipach */
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 0 6px rgba(0,0,0,.1);
  font-size: 13px;
  padding: 8px;
  margin-top: 8px;       /* niewielki odstęp od karty */
  opacity: 0;
  pointer-events: none;
  transition: opacity .25s ease;
  z-index: 20;
  white-space: pre-wrap;
}

/* pokazuj tooltip tylko przy najechaniu na całą kartę */
.god-card:hover .tooltip-card {
  opacity: 1;
}
</style>
