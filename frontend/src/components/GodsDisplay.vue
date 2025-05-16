<template>
  <div class="gods-container">
    <div
      v-for="god in gods"
      :key="god.name"
      class="god-card"
      :class="{ selected: selectedGodName === god.name, disabled: readonly }"
      @mouseenter="hoveredGod = god.name"
      @mouseleave="hoveredGod = null"
    >
      <!-- Ikona boga -->
      <img :src="`/img/icons/${god.name}.png`" alt="Ikona boga" class="god-icon" />

      <h3 class="god-name">{{ god.name }}</h3>

      <!-- Wybór poziomu -->
      <div class="levels">
        <button
          v-for="level in [1, 2, 3]"
          :key="level"
          :class="{ active: selectedGodName === god.name && selectedLevel === level }"
          @click="selectLevel(god.name, level)"
          :disabled="readonly"
        >
          Poziom {{ level }}
        </button>
      </div>

      <!-- Przycisk wyboru -->
      <button
        class="choose-btn"
        @click="confirmSelection(god.name)"
        :disabled="readonly || selectedGodName !== god.name || selectedLevel === null"
      >
        Wybierz
      </button>

      <!-- Dymek z opisem -->
      <div
        v-if="hoveredGod === god.name"
        class="tooltip"
      >
        {{ god.description }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    gods: Array,
    readonly: Boolean
  },
  data() {
    return {
      selectedGodName: null,
      selectedLevel: null,
      hoveredGod: null
    };
  },
  methods: {
    selectLevel(godName, level) {
      this.selectedGodName = godName;
      this.selectedLevel = level;
    },
    confirmSelection(godName) {
      if (this.selectedGodName && this.selectedLevel !== null) {
        this.$emit('choose-god', {
          godName: this.selectedGodName,
          level: this.selectedLevel
        });
      }
    }
  }
};
</script>

<style scoped>
.gods-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.god-card {
  position: relative;
  width: 180px;
  padding: 16px;
  border: 2px solid #ccc;
  border-radius: 12px;
  text-align: center;
  background-color: #f9f9f9;
  transition: transform 0.2s ease;
}

.god-card:hover {
  transform: scale(1.03);
}

.god-card.selected {
  border-color: #007BFF;
}

.god-card.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.god-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 8px;
}

.god-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
}

.levels {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 10px;
}

.levels button {
  padding: 4px 8px;
  border: 1px solid #ccc;
  background-color: #eee;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.levels button.active {
  background-color: #007BFF;
  color: white;
  border-color: #007BFF;
}

.choose-btn {
  margin-top: 6px;
  padding: 6px 12px;
  background-color: #28a745;
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: bold;
  cursor: pointer;
}

.choose-btn:hover:not(:disabled) {
  background-color: #218838;
}

.choose-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.tooltip {
  position: absolute;
  top: 10px;
  left: 100%;
  margin-left: 10px;
  padding: 8px;
  width: 180px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  text-align: left;
  z-index: 100;
}
</style>
