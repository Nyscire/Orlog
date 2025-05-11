<template>
  <div class="gods-container">
    <div
      v-for="god in validGods"
      :key="god.name"
      :class="['god-card', { selected: isSelected(god.name) }]"
      @click="handleClick(god.name)"
    >
      <img :src="getGodIcon(god.name)" :alt="god.name" />
      <div class="god-name">{{ god.name }}</div>
      <div class="god-desc">{{ god.description }}</div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    gods: { type: Array, default: () => [] },
    readonly: { type: Boolean, default: false }
  },
  computed: {
    validGods() {
      return this.gods.filter(g => g && g.name) // <--- zapobiega null
    }
  },
  methods: {
    getGodIcon(name) {
      return `/img/icons/${name}.png`
    },
    handleClick(name) {
      if (!this.readonly) this.$emit('choose-god', name)
    },
    isSelected(name) {
      const selected = this.gods.find(g => g && g.name === name && g.selected)
      return !!selected
    }
  }
}
</script>

<style scoped>
.gods-container {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}
.god-card {
  border: 2px solid transparent;
  padding: 0.5rem;
  text-align: center;
  width: 100px;
}
.god-card.selected {
  border-color: blue;
}
.god-card img {
  width: 64px;
  height: 64px;
}
</style>
