<template>
  <div class="player-stats">
    <div class="player-name">{{ name }}</div>
    <div class="stats">
      <div class="stat hp">HP: {{ hp }}</div>
      <div class="stat mana">Mana: {{ mana }}</div>
    </div>
    
  </div>
</template>

<script>
export default {
  props: {
  name: String,
  hp: Number,
  mana: Number,
}

}
</script>

<style scoped>
.player-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 1rem 0;
}
.player-name {
  font-weight: bold;
  font-size: 1.2rem;
}
.stats {
  display: flex;
  gap: 1rem;
  margin: 0.5rem 0;
}
.stat {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.gods-icons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.god-icon {
  width: 32px;
  height: 32px;
}
</style>
