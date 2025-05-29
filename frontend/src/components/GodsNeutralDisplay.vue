<template>
  <div class="gods-container">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card selected"
    >
      <img :src="`/img/icons/${god.name}.png`" alt="Ikona boga" class="god-icon" />
      <h3 class="god-name">{{ god.name }}</h3>

      <div class="chosen-level" v-if="god.level">
        <strong>Poziom: {{ god.level }}</strong>
      </div>

      <!-- Tooltip zawsze widoczny pod kartą jeśli jest wybrany poziom -->
      <div
  v-if="god.level !== null && god.level !== undefined && god.levels?.[god.level]"
  class="tooltip-visible"
>
  {{ god.levels[god.level] }}
</div>

    </div>
  </div>
</template>

<script>
export default {
  props: {
    gods: Array
  },
  

};
</script>

<style scoped>
@import "@/assets/GodCardStyles.css";

/* Styl dla tooltipa widocznego pod kartą */
.tooltip-visible {
  width: 180px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  text-align: center;
  margin: 10px auto 0; /* centrowanie pod kartą */
  padding: 8px 0;
}
</style>
