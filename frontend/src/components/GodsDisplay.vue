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
      <span class="tooltip-text">{{ god.description }}</span>
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
  border: 2px solid black;
  padding: 0.5rem;
  text-align: center;
  width: 100px;
  position: relative;
  cursor: pointer;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color: white;
}

.god-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.god-card.selected {
  border-color: #007bff;
}

.god-card img {
  width: 64px;
  height: 64px;
}

.god-name {
  font-weight: bold;
  margin-top: 0.25rem;
}

/* Tooltip */
.tooltip-text {
  visibility: hidden;
  opacity: 0;
  width: 160px;
  background-color: #333;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 0.5rem;
  position: absolute;
  top: 100%; /* tuż pod kartą */
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  transition: opacity 0.3s;
  pointer-events: none;
  z-index: 1;
}


.god-card:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}
.tooltip-text::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: transparent transparent #333 transparent;
}

</style>
