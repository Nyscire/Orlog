<template>
  <div class="dice-display">
    <h4 v-if="title">{{ title }}</h4>
    <div class="dice-grid">
      <Die
        v-for="(die, index) in dice"
        :key="index"
        :die="die"
        :selectable="selectable"
        :selected="isSelected(index)"
        @click="toggleSelection(index)"
      />
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
  max-width: 350px;
  margin: 0 auto;
}

.dice-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  justify-items: center;
  align-items: center;
  gap: 0.5rem;
  min-height: 52px; /* Ensure minimum height for dice */
  max-width: 180px; /* Limit width to accommodate 3 dice per row */
  margin: 0 auto;
}

h3,h4 {
  text-align: center;
}
</style>