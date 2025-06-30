<template>
  <div class="dice-display">
    <h4 v-if="title" class="dice-title">{{ title }}</h4>
    <div class="dice-container">
      <div class="dice-grid" >
        <transition-group name="dice-pop" tag="div" class="dice-wrapper">
          <Die
            v-for="(die, index) in dice"
            :key="`${die.stat}-${index}`"
            :die="die"
            :selectable="selectable"
            :selected="isSelected(index)"
            @click="toggleSelection(index)"
          />
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script>
import Die from './Die.vue'

export default {
  props: {
    dice: {
      type: Array,
      required: true
    },
    title: String,
    selectable: Boolean,
    selectedIndexes: Array
  },
  emits: ['toggle-selection'],
  components: { Die },
  methods: {
    isSelected(index) {
      return this.selectedIndexes?.includes(index)
    },
    toggleSelection(index) {
      if (this.selectable) {
        this.$emit('toggle-selection', index)
      }
    }
  }
}
</script>

<style scoped>
.dice-display {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
}

.dice-title {
  text-align: center;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1rem;
}

.dice-container {
  width: 100%;
  overflow: visible;
}

.dice-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  min-height: 60px;
  padding: 0.5rem;
}

.dice-wrapper {
  display: contents;
}

/* Handle many dice layout */
.dice-grid.many-dice {
  max-width: 100%;
  gap: 0.5rem;
}

.dice-grid.many-dice:has(> :nth-child(5)) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  justify-items: center;
}

.dice-grid.many-dice:has(> :nth-child(6)) {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
}

/* Alternative flex approach for better browser support */
@supports not selector(:has(*)) {
  .dice-grid.many-dice {
    display: flex;
    flex-wrap: wrap;
    max-width: 200px;
    margin: 0 auto;
  }
}

/* Animations */
.dice-pop-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.dice-pop-leave-active {
  transition: all 0.3s ease-in;
}

.dice-pop-enter-from {
  opacity: 0;
  transform: scale(0.3) rotate(180deg);
}

.dice-pop-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.dice-pop-move {
  transition: transform 0.4s ease;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .dice-grid {
    gap: 0.5rem;
  }
  
  .dice-grid.many-dice {
    max-width: 180px;
  }
}

@media (max-width: 768px) {
  .dice-grid {
    gap: 0.4rem;
  }
  
  .dice-grid.many-dice {
    max-width: 160px;
    gap: 0.3rem;
  }
}
</style>