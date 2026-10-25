<template>
  <div class="start-screen">
    <header class="hero">
      <div class="runes" aria-hidden="true">ᛟ ᚱ ᛚ ᛟ ᚷ</div>
      <h1 class="title">Orlog</h1>
      <p class="subtitle">Gra w kości dla dwóch wojowników</p>
      <div class="divider" aria-hidden="true"><span></span><i></i><span></span></div>
    </header>

    <section class="panel">
      <template v-if="!joined">
        <div v-if="gameInProgress" class="notice">
          Trwa partia: {{ lobby.players.join(' i ') }}. Jeśli to Ty, wpisz to samo imię, żeby wrócić do gry.
        </div>

        <label class="field-label" for="player-name">Twoje imię</label>
        <input
          id="player-name"
          v-model="name"
          class="name-input"
          maxlength="20"
          placeholder="np. Eivor"
          autocomplete="off"
          @keyup.enter="join"
        />

        <div class="gods-header">
          <span class="field-label">Bogowie, których zabierasz do gry</span>
          <span class="gods-counter" :class="{ full: selected.length === maxGods }">
            {{ selected.length }} / {{ maxGods }}
          </span>
        </div>
        <p class="hint">Ich łaski będziesz mógł wykupić maną w trakcie partii.</p>

        <div v-if="gods.length === 0" class="hint">Wczytuję bogów z serwera…</div>
        <div v-else class="gods-grid">
          <button
            v-for="god in gods"
            :key="god.name"
            type="button"
            class="god-option"
            :class="{ selected: isSelected(god), locked: isLocked(god) }"
            :aria-pressed="isSelected(god)"
            :disabled="isLocked(god)"
            @click="toggle(god)"
          >
            <span v-if="isSelected(god)" class="check" aria-hidden="true">✓</span>
            <img :src="`/img/icons/${god.name.toLowerCase()}.png`" alt="" class="god-icon" />
            <span class="god-name">{{ god.name }}</span>
            <span class="god-effect">{{ effect(god) }}</span>
            <span class="god-costs">Mana: {{ god.mana_costs.join(' / ') }}</span>
          </button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn btn-gold join-btn" :disabled="!canJoin" @click="join">
          {{ othersWaiting.length ? `Zagraj z: ${othersWaiting.join(', ')}` : 'Dołącz do gry' }}
        </button>
      </template>

      <div v-else class="waiting">
        <div class="waiting-runes" aria-hidden="true"><span>ᚠ</span><span>ᚢ</span><span>ᚦ</span></div>
        <h2>Czekamy na drugiego gracza</h2>
        <p>Grasz jako <strong>{{ playerName }}</strong>, bogowie: {{ chosenGods.join(', ') }}.</p>
        <p class="hint">Drugi gracz otwiera tę samą stronę i wpisuje swoje imię.</p>
        <button class="btn btn-ghost" @click="$emit('leave')">Zmień imię albo bogów</button>
      </div>
    </section>

    <footer class="status">
      <span class="dot" :class="connected ? 'ok' : 'off'"></span>
      {{ statusText }}
    </footer>
  </div>
</template>

<script>
const STORAGE_KEY = 'orlog.player'

export default {
  name: 'StartMenu',
  props: {
    lobby: {
      type: Object,
      default: null
    },
    connected: Boolean,
    joined: Boolean,
    playerName: {
      type: String,
      default: ''
    },
    chosenGods: {
      type: Array,
      default: () => []
    },
    error: String
  },
  emits: ['join', 'leave'],
  data() {
    return {
      name: '',
      selected: []
    }
  },
  computed: {
    gods() {
      return this.lobby?.gods || []
    },
    maxGods() {
      return this.lobby?.max_gods || 3
    },
    gameInProgress() {
      return !!this.lobby && this.lobby.stage !== 'waiting'
    },
    othersWaiting() {
      if (!this.lobby || this.gameInProgress) return []
      return this.lobby.players.filter(n => n !== this.playerName)
    },
    canJoin() {
      return this.connected && this.name.trim().length > 0 &&
        this.selected.length >= 1 && this.selected.length <= this.maxGods
    },
    statusText() {
      if (!this.connected) return 'Brak połączenia z serwerem. Sprawdź, czy backend działa (python main.py).'
      if (this.joined) return 'Połączono z serwerem'
      if (this.gameInProgress) return 'Połączono · na serwerze trwa partia'
      if (this.othersWaiting.length) return `Połączono · na rywala czeka: ${this.othersWaiting.join(', ')}`
      return 'Połączono · nikt jeszcze nie czeka'
    }
  },
  watch: {
    gods: {
      immediate: true,
      handler() {
        this.normalizeSelection()
      }
    }
  },
  mounted() {
    // ostatnie imię i bogowie z tej przeglądarki, żeby nie wybierać za każdym razem
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
      if (saved && typeof saved.name === 'string') this.name = saved.name
      if (saved && Array.isArray(saved.gods) && saved.gods.length) this.selected = saved.gods
    } catch (e) {
      // brak dostępu do localStorage nie przeszkadza w grze
    }
    this.normalizeSelection()
  },
  methods: {
    normalizeSelection() {
      if (!this.gods.length) return
      const names = this.gods.map(g => g.name)
      this.selected = this.selected.filter(n => names.includes(n)).slice(0, this.maxGods)
      if (!this.selected.length) this.selected = names.slice(0, this.maxGods)
    },
    isSelected(god) {
      return this.selected.includes(god.name)
    },
    isLocked(god) {
      return !this.isSelected(god) && this.selected.length >= this.maxGods
    },
    toggle(god) {
      if (this.isSelected(god)) this.selected = this.selected.filter(n => n !== god.name)
      else if (this.selected.length < this.maxGods) this.selected = [...this.selected, god.name]
    },
    effect(god) {
      return god.description.split('\n').filter(line => !line.startsWith('Koszt')).join(' ')
    },
    join() {
      if (!this.canJoin) return
      const player = { name: this.name.trim(), gods: [...this.selected] }
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(player))
      } catch (e) {
        // jak wyżej
      }
      this.$emit('join', player)
    }
  }
}
</script>

<style scoped>
.start-screen {
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1.25rem 1rem;
  color: var(--parchment);
}

.hero {
  text-align: center;
}

.runes {
  color: var(--gold);
  letter-spacing: 0.6em;
  font-size: 1rem;
  opacity: 0.8;
}

.title {
  margin: 0.1rem 0 0;
  font-family: var(--font-title);
  font-weight: 900;
  font-size: clamp(2.75rem, 7vw, 4.5rem);
  line-height: 1;
  letter-spacing: 0.08em;
  color: var(--gold-bright);
  text-shadow: 0 3px 0 rgba(0, 0, 0, 0.6), 0 0 28px rgba(230, 194, 112, 0.25);
}

.subtitle {
  margin: 0.35rem 0 0;
  font-family: var(--font-title);
  font-size: 1rem;
  letter-spacing: 0.12em;
  color: var(--parchment-2);
}

.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.6rem;
}

.divider span {
  width: 90px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold));
}

.divider span:last-child {
  background: linear-gradient(90deg, var(--gold), transparent);
}

.divider i {
  width: 8px;
  height: 8px;
  background: var(--gold);
  transform: rotate(45deg);
}

.panel {
  width: min(760px, 100%);
  box-sizing: border-box;
  padding: 1.25rem 1.5rem;
  color: var(--ink);
  background: linear-gradient(180deg, #f8f0de 0%, var(--parchment) 60%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5), inset 0 0 0 4px rgba(255, 255, 255, 0.35);
}

.notice {
  margin-bottom: 1rem;
  padding: 0.6rem 0.8rem;
  background: rgba(47, 93, 124, 0.12);
  border-left: 3px solid var(--rune);
  border-radius: 6px;
  font-size: 0.9rem;
}

.field-label {
  display: block;
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.06em;
  color: var(--ink-soft);
}

.name-input {
  display: block;
  width: 100%;
  box-sizing: border-box;
  margin: 0.4rem 0 1rem;
  padding: 0.6rem 0.9rem;
  font: inherit;
  font-size: 1.1rem;
  color: var(--ink);
  background: #fffaf0;
  border: 1.5px solid var(--edge);
  border-radius: 8px;
}

.name-input:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(201, 162, 76, 0.35);
}

.gods-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.gods-counter {
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: var(--parchment-3);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--ink-soft);
  white-space: nowrap;
}

.gods-counter.full {
  background: var(--gold);
  color: var(--wood-900);
}

.hint {
  margin: 0.25rem 0 0.75rem;
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.gods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 0.75rem;
}

.god-option {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 0.75rem 0.75rem 0.7rem;
  font: inherit;
  color: var(--ink);
  text-align: center;
  background: #fbf5e6;
  border: 1.5px solid var(--parchment-3);
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.god-option:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: var(--edge);
}

.god-option.selected {
  background: #fff4d6;
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(201, 162, 76, 0.45), 0 6px 14px rgba(140, 106, 44, 0.2);
}

.god-option.locked {
  opacity: 0.45;
  cursor: not-allowed;
}

.check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 900;
  color: var(--wood-900);
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
  border: 1px solid var(--gold-dark);
}

.god-icon {
  width: 46px;
  height: 46px;
}

.god-name {
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 1.1rem;
}

.god-effect {
  font-size: 0.85rem;
  line-height: 1.3;
}

.god-costs {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.error {
  margin: 1rem 0 0;
  color: var(--blood);
  font-weight: 600;
}

.join-btn {
  display: block;
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  font-size: 1.05rem;
}

.waiting {
  text-align: center;
  padding: 0.5rem 0;
}

.waiting h2 {
  margin: 0.5rem 0;
  font-family: var(--font-title);
  font-size: 1.4rem;
}

.waiting p {
  margin: 0.4rem 0;
}

.waiting .btn {
  margin-top: 0.75rem;
}

.waiting-runes {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  font-size: 1.8rem;
  color: var(--gold-dark);
}

.waiting-runes span {
  animation: runePulse 1.5s ease-in-out infinite;
}

.waiting-runes span:nth-child(2) {
  animation-delay: 0.25s;
}

.waiting-runes span:nth-child(3) {
  animation-delay: 0.5s;
}

@keyframes runePulse {
  0%, 100% { opacity: 0.25; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-4px); }
}

.status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--parchment-2);
  text-align: center;
}

.dot {
  flex: 0 0 auto;
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.dot.ok {
  background: #7cc46a;
  box-shadow: 0 0 6px #7cc46a;
}

.dot.off {
  background: #e05a4f;
  box-shadow: 0 0 6px #e05a4f;
}

@media (max-width: 600px) {
  .panel {
    padding: 1.1rem;
  }

  .gods-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}
</style>
