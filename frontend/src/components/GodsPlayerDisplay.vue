<template>
  <div class="gods-display">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card"
      :class="{ selected: isSelected(god) }"
      style="position: relative;"
    >
      <h3>{{ god.name }}</h3>
      <img :src="`/img/icons/${god.name}.png`" alt="Ikona boga" class="god-icon" />

      <div class="level-buttons" v-if="!readonly">
        <button
          v-for="level in [1, 2, 3]"
          :key="level"
          :class="{ active: god.level === level }"
          @click="selectLevel(god.name, level)"
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

      <!-- Opis wybranego poziomu osobno -->
      <div class="level-description" v-if="god.level">
        <strong>Wybrany poziom {{ god.level }}:</strong>
        <p>{{ god.levels[god.level - 1] }}</p>
      </div>

      <!-- Tooltip: OGÓLNY opis boga zawsze ten sam, widoczny przy hover -->
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
    chosenGod: Object
  },
  methods: {
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
@import "@/assets/GodCardStyles.css";

.gods-display {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  height: 262px;
}
.god-card {
  border: 2px solid #ccc;
  border-radius: 0.5rem;
  padding: 1rem;
  width: 200px;
  background: #fff;
  position: relative; /* dla tooltipa */
}
.god-card.selected {
  border-color: #333;
  background: #d1d8d8;
}
.level-buttons {
  margin-top: 1rem;
  display: flex;
  flex-wrap: nowrap;
  gap: 0.25rem;
  justify-content: center;
  align-items: center;
  flex-direction: row;
}

.level-buttons button {
  padding: 0.2rem 0.4rem;
  font-size: 0.8rem;
  cursor: pointer;
  border-radius: 0.25rem;
  border: 1px solid #aaa;
  background-color: #f9f9f9;
}

.level-buttons button.active {
  font-weight: bold;
  background-color: #ddf;
}

.confirm-btn {
  font-weight: bold;
  background-color: #cce;
}

.level-description {
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

/* Tooltip – domyślnie ukryty i absolutnie pozycjonowany */
.tooltip-card {
  position: absolute;
  bottom: 100%;          /* Tooltip pojawia się nad kartą */
  left: 50%;
  transform: translateX(-50%);
  width: 180px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  padding: 8px;
  margin-bottom: 8px;    /* odstęp od karty, ale od góry */
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
  z-index: 20;
  white-space: pre-wrap;
}


/* Pokaż tooltip przy hover na kartę */
.god-card:hover .tooltip-card {
  opacity: 1;
  pointer-events: auto;
}
</style>
