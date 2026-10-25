<template>
  <div class="event-log">
    <div class="log-title">Przebieg gry</div>
    <div class="log-body" ref="body">
      <div v-if="rounds.length === 0" class="log-empty">
        Tu pojawią się ruchy graczy i wyniki walk.
      </div>
      <div v-for="r in rounds" :key="r.round" class="log-round">
        <div class="round-label">Runda {{ r.round }}</div>
        <div
          v-for="(entry, i) in r.entries"
          :key="i"
          class="log-entry"
          :class="`kind-${entry.kind}`"
        >
          {{ entry.text }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventLog',
  props: {
    entries: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    rounds() {
      const groups = []
      for (const entry of this.entries) {
        const last = groups[groups.length - 1]
        if (last && last.round === entry.round) last.entries.push(entry)
        else groups.push({ round: entry.round, entries: [entry] })
      }
      return groups
    }
  },
  // najnowsze wpisy są na dole, więc po każdej zmianie przewijamy do końca
  watch: {
    entries() {
      this.$nextTick(this.scrollToEnd)
    }
  },
  mounted() {
    this.scrollToEnd()
  },
  methods: {
    scrollToEnd() {
      const el = this.$refs.body
      if (el) el.scrollTop = el.scrollHeight
    }
  }
}
</script>

<style scoped>
.event-log {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  padding: 0.4rem 0.75rem;
  box-sizing: border-box;
}

.log-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #8d6e63;
  margin-bottom: 0.25rem;
}

.log-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  font-size: 0.8rem;
  line-height: 1.35;
  color: #3e2723;
}

.log-empty {
  color: #8d6e63;
  font-style: italic;
}

.log-round + .log-round {
  margin-top: 0.35rem;
  padding-top: 0.35rem;
  border-top: 1px solid #f0e0c0;
}

.round-label {
  font-weight: 700;
  font-size: 0.75rem;
  color: #6d4c41;
}

.log-entry.kind-round {
  color: #8d6e63;
}

.log-entry.kind-god {
  color: #6a1b9a;
}

.log-entry.kind-battle {
  color: #b71c1c;
}

.log-entry.kind-win {
  font-weight: 700;
  color: #2e7d32;
}
</style>
