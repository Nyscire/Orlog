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
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid var(--parchment-3);
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  box-sizing: border-box;
}

.log-title {
  font-family: var(--font-title);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--ink-soft);
  margin-bottom: 0.25rem;
}

.log-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  font-size: 0.8rem;
  line-height: 1.35;
  color: var(--ink);
}

.log-empty {
  color: var(--ink-soft);
  font-style: italic;
}

.log-round + .log-round {
  margin-top: 0.35rem;
  padding-top: 0.35rem;
  border-top: 1px solid var(--parchment-3);
}

.round-label {
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.75rem;
  color: var(--gold-dark);
}

/* kolorowa kropka zamiast kolorowego tekstu, żeby dało się to czytać */
.log-entry {
  position: relative;
  padding-left: 0.8rem;
}

.log-entry::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.45em;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--edge);
}

.log-entry.kind-round {
  color: var(--ink-soft);
}

.log-entry.kind-dice::before {
  background: var(--rune);
}

.log-entry.kind-god::before {
  background: var(--violet);
}

.log-entry.kind-battle::before {
  background: var(--blood);
}

.log-entry.kind-win {
  font-weight: 700;
  color: var(--moss);
}

.log-entry.kind-win::before {
  background: var(--moss);
}
</style>
