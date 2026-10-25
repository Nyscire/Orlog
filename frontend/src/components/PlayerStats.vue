<template>
  <div class="player-stats">
    <div class="player-name">{{ name }}</div>
    <div class="stats">
      <div class="stat hp">HP: {{ hp }}</div>
      <div class="stat mana" :title="pendingMana ? 'Mana z zachowanych kości trafi do puli przed walką' : ''">
        Mana: {{ mana }}<span v-if="pendingMana" class="pending"> (+{{ pendingMana }})</span>
      </div>
    </div>
    
  </div>
</template>

<script>
export default {
  props: {
  name: String,
  hp: Number,
  mana: Number,
  pendingMana: {
    type: Number,
    default: 0
  }
}

}
</script>

<style scoped>
/* nazwa i statystyki w jednym rzędzie, żeby nie zabierały wysokości */
.player-stats {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.player-name {
  font-weight: bold;
  font-size: 1.1rem;
  margin-right: 0.25rem;
}
.stats {
  display: flex;
  gap: 0.5rem;
}
.stat {
  padding: 0.25rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  white-space: nowrap;
}
.pending {
  color: #6f42c1;
  font-weight: 600;
}
</style>
