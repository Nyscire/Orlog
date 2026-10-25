<template>
  <div class="player-stats">
    <div class="player-name">{{ name }}</div>
    <div class="stats">
      <div class="stat hp" :class="hpLevel" :title="`Życie: ${hp} z ${maxHp}. Kto spadnie do zera, przegrywa.`">
        <span class="label">HP</span>
        <strong>{{ hp }}</strong>
        <span class="hp-bar"><span class="hp-fill" :style="{ width: hpPercent + '%' }"></span></span>
      </div>
      <div class="stat mana" title="Mana: waluta, za którą kupujesz łaski bogów. Mana z odłożonych kości dochodzi przed walką.">
        <span class="mana-dot"></span>
        <span class="label">Mana</span>
        <strong>{{ mana }}</strong>
        <span v-if="pendingMana" class="pending">+{{ pendingMana }} z kości</span>
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
  },
  maxHp: {
    type: Number,
    default: 21
  }
},
computed: {
  hpPercent() {
    return Math.max(0, Math.min(100, Math.round((this.hp || 0) / this.maxHp * 100)))
  },
  hpLevel() {
    if (this.hp > this.maxHp / 2) return 'hp-ok'
    if (this.hp > this.maxHp / 4) return 'hp-mid'
    return 'hp-low'
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
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 1.15rem;
  margin-right: 0.25rem;
}
.stats {
  display: flex;
  gap: 0.5rem;
}
.stat {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  color: var(--ink);
  background: #fbf5e6;
  border: 1px solid var(--edge);
  border-radius: 6px;
  white-space: nowrap;
  font-size: 0.9rem;
}
.label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--ink-soft);
}
.hp-bar {
  width: 46px;
  height: 6px;
  border-radius: 3px;
  background: rgba(43, 29, 18, 0.15);
  overflow: hidden;
}
.hp-fill {
  display: block;
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.hp-ok .hp-fill { background: var(--moss); }
.hp-mid .hp-fill { background: var(--gold); }
.hp-low .hp-fill { background: var(--blood); }
.hp-low strong { color: var(--blood); }
.mana-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #aab4ff, var(--mana));
  box-shadow: 0 0 4px rgba(79, 95, 176, 0.6);
}
.pending {
  color: var(--mana);
  font-weight: 700;
  margin-left: 0.15rem;
}
</style>
