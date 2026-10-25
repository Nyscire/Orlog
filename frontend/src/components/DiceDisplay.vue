<template>
  <div class="dice-display" :class="{ compact, labeled: labels }">
    <h4 v-if="title">{{ title }}</h4>
    <div class="dice-grid">
      <Die
        v-for="(die, index) in dice"
        :key="index"
        :die="die"
        :selectable="selectable"
        :selected="isSelected(index)"
        :label="labels"
        :tooltip-placement="tooltipPlacement"
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
    // mniejsze kości, np. dla przeciwnika i strefy środkowej
    compact: Boolean,
    // podpisy pod kośćmi
    labels: Boolean,
    tooltipPlacement: {
      type: String,
      default: 'above'
    },
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
  --die-size: 56px;
  width: 100%;
}

.dice-display.compact {
  --die-size: 44px;
}

/* wszystkie kości w jednym rzędzie, zawijają się dopiero na wąskim ekranie */
.dice-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  min-height: var(--die-size);
}

.compact .dice-grid {
  gap: 0.35rem;
}

/* miejsce na podpisy pod kośćmi */
.labeled .dice-grid {
  row-gap: 1.3rem;
  padding-bottom: 0.95rem;
}

h3,h4 {
  text-align: center;
  margin: 0 0 0.35rem;
  font-family: var(--font-title);
  font-size: 0.8rem;
  letter-spacing: 0.04em;
}
</style>