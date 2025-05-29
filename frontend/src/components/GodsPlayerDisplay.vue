<template>
  <div class="gods-display">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card"
      :class="{ selected: isSelected(god) }"
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

      <div class="level-description" v-if="god.level">
        <strong>Wybrany poziom {{ god.level }}:</strong>
        <p>{{ god.levels[god.level-1] }}</p>
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
}
,
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
  flex-direction: row; /* zmienione z column na row */
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
</style>
