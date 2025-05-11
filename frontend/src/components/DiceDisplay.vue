<template>
  <div class="dice-container">
    <div
      v-for="(die, index) in dice"
      :key="index"
      :class="['die', { selected: isSelected(index), mana: die.gives_mana }]"
      @click="toggleSelection(index)"
    >
      <img :src="getDieIcon(die.stat)" :alt="die.stat" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    dice: { type: Array, required: true },
    title: String,
    selectable: { type: Boolean, default: false }
  },
  emits: ['toggle-selection'],
  data() {
    return {
      selectedIndexes: []
    }
  },
  methods: {
    toggleSelection(index) {
      if (!this.selectable) return
      this.$emit('toggle-selection', index)
    },
    isSelected(index) {
      return this.selectable && this.$parent.selectedDiceIndexes?.includes(index)
    },
    getDieIcon(stat) {
      return `/img/icons/${stat}.svg`
    }
  }
}
</script>

<style scoped>
.dice-container {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin: 1rem 0;
}

.die {
  width: 64px;
  height: 64px;
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 4px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.die img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* tylko mana */
.die.mana {
  border-color: black;
}

/* tylko selected */
.die.selected {
  border-color: red;
}

/* mana + selected = fioletowy */
.die.mana.selected {
  box-shadow: 0 0 0 3px black;
  border-color:black ;
}

</style>
