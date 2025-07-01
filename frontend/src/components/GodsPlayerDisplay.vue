<template>
  <div class="gods-display">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card"
      :class="{ selected: isSelected(god) }"
    >
      <h3 class="god-name">{{ god.name }}</h3>
      <img :src="`/img/icons/${god.name}.png`" alt="Ikona boga" class="god-icon" />

      <div class="level-buttons" v-if="!readonly">
        <button
          v-for="level in [1, 2, 3]"
          :key="level"
          :class="{ active: god.level === level }"
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

      <!-- Opis wybranego poziomu -->
      <div class="level-description" v-if="god.level && !readonly">
        <strong>Poziom {{ god.level }}:</strong>
        <p>{{ god.levels[god.level - 1] }}</p>
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
.gods-display {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
  height: 100%;
  overflow-y: auto;
  padding: 0.25rem;
}

.god-card {
  border: 2px solid #ccc;
  border-radius: 8px;
  padding: 0.75rem;
  width: 160px;
  max-height: 140px;
  background: #fff;
  position: relative;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.god-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.god-card.selected {
  border-color: #007bff;
  background: #e7f3ff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.god-name {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  text-align: center;
  color: #495057;
}

.god-icon {
  width: 36px;
  height: 36px;
  margin-bottom: 0.5rem;
}

.level-buttons {
  display: flex;
  gap: 0.25rem;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}

.level-btn {
  padding: 0.2rem 0.4rem;
  font-size: 0.75rem;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid #aaa;
  background-color: #f8f9fa;
  transition: all 0.2s ease;
  min-width: 24px;
}

.level-btn:hover {
  background-color: #e9ecef;
}

.level-btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.confirm-btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  font-weight: bold;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #218838;
}

.confirm-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.level-description {
  margin-top: 0.5rem;
  font-size: 0.7rem;
  text-align: center;
  max-height: 40px;
  overflow: hidden;
}

.level-description p {
  margin: 0.25rem 0 0 0;
  line-height: 1.2;
}

/* Tooltip */
.tooltip-card {
  position: absolute;
  bottom: 100%;
}

</style>