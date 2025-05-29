<template>
  <div class="god-card neutral-god-card">
    <h4 class="god-name">{{ god.name }}</h4>
    <img :src="`/img/icons/${god.name}.png`" alt="Ikona boga" class="god-icon" />

    <!-- Tooltip – wyświetlany przy hover -->
    <div class="tooltip-card">
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
    }
  }
}
</script>

<style scoped>
.god-card {
  position: relative;
  overflow: visible;
  border: 2px solid #ccc;
  border-radius: 0.5rem;
  padding: 1rem;
  padding-top: 0;
  width: 150px;
  background: #fff;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.god-icon {
  max-width: 50px;
  max-height: 50px;
  margin: 0.5rem 0;
}

.god-name {
  margin-top: 0.5rem;
  font-size: 1.1rem;
}

.tooltip-card {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 180px;
  background: #fff;
  border: 1px solid #ddd;
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
}

.god-card:hover .tooltip-card {
  opacity: 1;
}
</style>
