<template>
  <div class="start-screen">
    <div class="lang-switch" role="group" aria-label="Język / Language">
      <button
        v-for="lang in languages"
        :key="lang.id"
        type="button"
        :class="{ active: lang.id === locale }"
        :aria-pressed="lang.id === locale"
        @click="setLanguage(lang.id)"
      >
        {{ lang.id.toUpperCase() }}
      </button>
    </div>

    <header class="hero">
      <div class="runes" aria-hidden="true">ᛟ ᚱ ᛚ ᛟ ᚷ</div>
      <h1 class="title">Orlog</h1>
      <p class="subtitle">{{ $t('menu.subtitle') }}</p>
      <div class="divider" aria-hidden="true"><span></span><i></i><span></span></div>
    </header>

    <!-- lista stołów: po lewej gracz i bogowie, po prawej stoły -->
    <section v-if="!seated" class="panel lobby-panel">
      <div v-if="notice" class="notice">{{ notice }}</div>

      <div class="lobby">
        <div class="you">
          <label class="field-label" for="player-name">{{ $t('menu.yourName') }}</label>
          <input
            id="player-name"
            v-model="name"
            class="name-input"
            maxlength="20"
            :placeholder="$t('menu.namePlaceholder')"
            autocomplete="off"
          />

          <div class="gods-header">
            <span class="field-label">{{ $t('menu.godsLabel') }}</span>
            <span class="gods-counter" :class="{ full: selected.length === maxGods }">
              {{ selected.length }} / {{ maxGods }}
            </span>
          </div>

          <div v-if="gods.length === 0" class="hint">{{ $t('menu.loadingGods') }}</div>
          <template v-else>
            <div class="gods-grid" @mouseleave="hovered = null">
              <button
                v-for="god in gods"
                :key="god.name"
                type="button"
                class="god-option"
                :class="{ selected: isSelected(god), locked: isLocked(god), focused: detailGod && detailGod.name === god.name }"
                :aria-pressed="isSelected(god)"
                :aria-label="`${$t('gods.name', god)}: ${$t('gods.favor', god)}`"
                @click="toggle(god)"
                @mouseenter="hovered = god.name"
                @focus="hovered = god.name"
              >
                <span v-if="isSelected(god)" class="check" aria-hidden="true">✓</span>
                <img :src="icon(god)" alt="" class="god-icon" />
                <span class="god-name">{{ $t('gods.name', god) }}</span>
                <span class="god-favor">{{ $t('gods.favor', god) }}</span>
              </button>
            </div>

            <!-- opis boga pod kursorem (albo ostatnio wybranego) -->
            <div v-if="detailGod" class="god-detail" aria-live="polite">
              <img :src="icon(detailGod)" alt="" class="detail-icon" />
              <div class="detail-text">
                <div class="detail-head">
                  <strong>{{ $t('gods.favor', detailGod) }}</strong>
                  <span class="detail-phase">{{ $t('gods.phase.' + detailGod.phase) }}</span>
                  <span class="detail-costs">{{ $t('menu.costs', { costs: detailGod.mana_costs.join(' / ') }) }}</span>
                </div>
                <div>{{ $t('gods.describe', detailGod) }}</div>
              </div>
            </div>
          </template>
        </div>

        <div class="tables-col">
          <div class="tables-inner">
            <div class="tables-header">
              <span class="field-label">{{ $t('lobby.title') }}</span>
              <span class="tables-count">{{ $t('lobby.count', { n: tables.length }) }}</span>
            </div>

            <form class="create-form" @submit.prevent="createTable">
              <input
                v-model="tableName"
                class="table-name-input"
                maxlength="30"
                :placeholder="$t('lobby.namePlaceholder')"
                :aria-label="$t('lobby.namePlaceholder')"
                autocomplete="off"
              />
              <button type="submit" class="btn btn-gold create-btn" :disabled="!canSit || serverFull">
                {{ $t('lobby.create') }}
              </button>
            </form>

            <p v-if="error" class="error">{{ error }}</p>
            <p v-else-if="serverFull" class="hint">{{ $t('lobby.full', { max: lobby.max_tables }) }}</p>
            <p v-else-if="!canSit && connected" class="hint">{{ $t('lobby.needSetup') }}</p>

            <ul v-if="tables.length" class="tables-list">
              <li v-for="table in tables" :key="table.id" class="table-row" :class="{ open: table.open }">
                <div class="table-main">
                  <div class="table-title">
                    <span class="table-name">{{ tableTitle(table) }}</span>
                    <span class="table-code">#{{ table.id }}</span>
                  </div>
                  <div class="table-meta">{{ tableStatus(table) }}</div>
                </div>
                <button
                  v-if="table.open"
                  type="button"
                  class="btn btn-gold join-btn"
                  :disabled="!canSit"
                  @click="joinTable(table)"
                >
                  {{ $t('lobby.join') }}
                </button>
                <span v-else class="table-busy">{{ $t('lobby.busy') }}</span>
              </li>
            </ul>
            <div v-else class="tables-empty">
              <span class="empty-rune" aria-hidden="true">ᛟ</span>
              {{ $t('lobby.empty') }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- przy stole, czekamy na rywala -->
    <section v-else class="panel waiting-panel">
      <div class="waiting">
        <div class="waiting-runes" aria-hidden="true"><span>ᚠ</span><span>ᚢ</span><span>ᚦ</span></div>
        <div v-if="table" class="table-badge">{{ tableTitle(table) }} <span class="table-code">#{{ table.id }}</span></div>
        <div v-if="notice" class="notice">{{ notice }}</div>
        <h2>{{ $t('menu.waitingTitle') }}</h2>
        <p>{{ $t('menu.playingAs') }} <strong>{{ playerName }}</strong>, {{ $t('menu.withGods', { gods: myGodsText }) }}</p>
        <p class="hint">{{ $t('menu.waitingHint') }}</p>
        <button class="btn btn-ghost" @click="$emit('leave')">{{ $t('lobby.leave') }}</button>
      </div>
    </section>

    <footer class="status">
      <span class="dot" :class="connected ? 'ok' : 'off'"></span>
      {{ statusText }}
      <span class="sep">·</span>
      <button class="link-btn" @click="$emit('help')">{{ $t('menu.howToPlay') }}</button>
      <span class="sep">·</span>
      <button class="link-btn" @click="$emit('settings')">{{ $t('menu.settings') }}</button>
      <template v-if="canOpenWindow">
        <span class="sep">·</span>
        <button class="link-btn" :title="$t('settings.newWindowHint')" @click="newWindow">{{ $t('menu.newWindow') }}</button>
      </template>
      <template v-if="version">
        <span class="sep">·</span>
        <span class="version">v{{ version }}</span>
      </template>
    </footer>
  </div>
</template>

<script>
import { LANGUAGES, setSetting, settings } from '../settings'
import { godIcon } from '../dice'
import { appVersion, canOpenWindow, isApp, openPlayerWindow, serverUrl } from '../server'

const STORAGE_KEY = 'orlog.player'

export default {
  name: 'StartMenu',
  props: {
    // lista stołów z serwera: { tables, gods, max_gods, max_tables, full }
    lobby: {
      type: Object,
      default: null
    },
    connected: Boolean,
    seated: Boolean,
    playerName: {
      type: String,
      default: ''
    },
    // stół, przy którym siedzi gracz: { id, name, host }
    table: {
      type: Object,
      default: null
    },
    myGods: {
      type: Array,
      default: () => []
    },
    error: String,
    // np. przeciwnik wstał od stołu albo miejsce wygasło
    notice: String
  },
  emits: ['create-table', 'join-table', 'leave', 'help', 'settings'],
  data() {
    return {
      name: '',
      tableName: '',
      selected: [],
      hovered: null,
      lastPicked: null
    }
  },
  computed: {
    languages() {
      return LANGUAGES
    },
    locale() {
      return settings.locale
    },
    gods() {
      return this.lobby?.gods || []
    },
    tables() {
      return this.lobby?.tables || []
    },
    maxGods() {
      return this.lobby?.max_gods || 3
    },
    serverFull() {
      return !!this.lobby?.full
    },
    detailGod() {
      const name = this.hovered || this.lastPicked || this.selected[0]
      return this.gods.find(g => g.name === name) || this.gods[0] || null
    },
    myGodsText() {
      return this.myGods.map(name => this.$t('gods.name', { name })).join(', ')
    },
    version() {
      return appVersion
    },
    canOpenWindow() {
      return canOpenWindow
    },
    canSit() {
      return this.connected && this.name.trim().length > 0 &&
        this.selected.length >= 1 && this.selected.length <= this.maxGods
    },
    statusText() {
      if (!this.connected) {
        if (!serverUrl()) return this.$t('menu.status.noServer')
        return isApp ? this.$t('menu.status.offlineApp', { server: serverUrl() }) : this.$t('menu.status.offline')
      }
      if (this.seated) return this.$t('menu.status.joined')
      return this.$t('menu.status.online', { tables: this.$t('lobby.count', { n: this.tables.length }) })
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
    icon(god) {
      return godIcon(god.name)
    },
    isSelected(god) {
      return this.selected.includes(god.name)
    },
    isLocked(god) {
      return !this.isSelected(god) && this.selected.length >= this.maxGods
    },
    toggle(god) {
      // przy komplecie kliknięcie innego boga podmienia najdawniej wybranego
      if (this.isSelected(god)) this.selected = this.selected.filter(n => n !== god.name)
      else if (this.selected.length < this.maxGods) this.selected = [...this.selected, god.name]
      else this.selected = [...this.selected.slice(1), god.name]
      this.lastPicked = god.name
    },
    newWindow() {
      openPlayerWindow()
    },
    setLanguage(id) {
      setSetting('locale', id)
    },
    tableTitle(table) {
      return table.name || this.$t('lobby.defaultName', { host: table.host })
    },
    tableStatus(table) {
      const players = table.players.join(' vs ')
      if (table.stage === 'waiting') return this.$t('lobby.waitingFor', { name: table.players[0] || '' })
      if (table.stage === 'finished') return this.$t('lobby.finished', { players })
      return this.$t('lobby.playing', { players, round: table.round })
    },
    // imię i bogowie, z którymi gracz siada przy stole (zapamiętane na następny raz)
    player() {
      const player = { name: this.name.trim(), gods: [...this.selected] }
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(player))
      } catch (e) {
        // jak wyżej
      }
      return player
    },
    createTable() {
      if (!this.canSit || this.serverFull) return
      this.$emit('create-table', { ...this.player(), tableName: this.tableName.trim() })
    },
    joinTable(table) {
      if (!this.canSit || !table.open) return
      this.$emit('join-table', { ...this.player(), table: table.id })
    }
  }
}
</script>

<style scoped>
.lang-switch {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  border: 1px solid var(--gold-dark);
  border-radius: 999px;
  overflow: hidden;
}

.lang-switch button {
  padding: 0.3rem 0.75rem;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--on-bg-soft);
  background: transparent;
  border: none;
  cursor: pointer;
}

.lang-switch button.active {
  color: var(--on-accent);
  background: var(--gold);
}

.start-screen {
  position: relative;
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1.25rem 1rem;
  color: var(--on-bg);
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
  text-shadow: 0 3px 0 rgba(0, 0, 0, 0.6), 0 0 28px rgba(var(--accent-rgb), 0.25);
}

.subtitle {
  margin: 0.35rem 0 0;
  font-family: var(--font-title);
  font-size: 1rem;
  letter-spacing: 0.12em;
  color: var(--on-bg-soft);
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
  width: min(920px, 100%);
  box-sizing: border-box;
  padding: 1.25rem 1.5rem;
  color: var(--ink);
  background: linear-gradient(180deg, var(--panel-top) 0%, var(--parchment) 60%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5), inset 0 0 0 4px var(--glass);
}

.notice {
  margin-bottom: 1rem;
  padding: 0.6rem 0.8rem;
  background: var(--glass-2);
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
  background: var(--input-bg);
  border: 1.5px solid var(--edge);
  border-radius: 8px;
}

.name-input:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.35);
}

.gods-header,
.tables-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
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
  color: var(--on-accent);
}

.hint {
  margin: 0.25rem 0 0.75rem;
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.gods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(112px, 1fr));
  gap: 0.45rem;
}

.god-option {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
  min-width: 0;
  padding: 0.45rem 0.3rem 0.4rem;
  font: inherit;
  color: var(--ink);
  text-align: center;
  background: var(--card);
  border: 1.5px solid var(--parchment-3);
  border-radius: 9px;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.god-option:hover,
.god-option.focused {
  transform: translateY(-2px);
  border-color: var(--edge);
}

.god-option.selected {
  background: var(--card-hi);
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.45), 0 6px 14px rgba(var(--accent-rgb), 0.2);
}

/* przy komplecie pozostali są przygaszeni, ale klik podmienia wybór */
.god-option.locked {
  opacity: 0.55;
}

.god-option.locked:hover {
  opacity: 0.85;
}

.check {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 900;
  color: var(--on-accent);
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
  border: 1px solid var(--gold-dark);
}

.god-icon {
  width: 30px;
  height: 30px;
  filter: var(--icon-filter);
}

.god-name {
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.95rem;
  line-height: 1.15;
}

.god-favor {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.68rem;
  color: var(--ink-soft);
}

.god-detail {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 2.9rem;
  margin-top: 0.5rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  line-height: 1.3;
  background: var(--glass);
  border: 1px solid var(--parchment-3);
  border-radius: 8px;
}

.detail-text {
  flex: 1;
  min-width: 0;
}

.detail-icon {
  flex: 0 0 auto;
  width: 34px;
  height: 34px;
  filter: var(--icon-filter);
}

.detail-head {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.2rem 0.6rem;
}

.detail-head strong {
  font-family: var(--font-title);
}

.detail-phase {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--ink-soft);
}

.detail-costs {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--ink-soft);
}

.error {
  margin: 0.25rem 0 0.5rem;
  font-size: 0.85rem;
  color: var(--blood);
  font-weight: 600;
}

/* ---------- lista stołów ---------- */

.lobby-panel {
  width: min(1180px, 100%);
}

.waiting-panel {
  width: min(620px, 100%);
}

.lobby {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, 1fr);
  gap: 1.5rem;
}

/* prawa kolumna ma wysokość lewej, a lista stołów przewija się w środku */
.tables-col {
  position: relative;
  min-height: 18rem;
  padding-left: 1.5rem;
  border-left: 1px solid var(--parchment-3);
}

.tables-inner {
  position: absolute;
  inset: 0 0 0 1.5rem;
  display: flex;
  flex-direction: column;
}

.tables-count {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--ink-soft);
}

.create-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.table-name-input {
  flex: 1;
  min-width: 0;
  padding: 0.45rem 0.75rem;
  font: inherit;
  font-size: 0.95rem;
  color: var(--ink);
  background: var(--input-bg);
  border: 1.5px solid var(--edge);
  border-radius: 8px;
}

.table-name-input:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.35);
}

.create-btn {
  flex: 0 0 auto;
  padding: 0.45rem 1rem;
  white-space: nowrap;
}

.tables-list {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  margin: 0.25rem 0 0;
  padding: 0 0.15rem 0 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.table-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.65rem;
  background: var(--glass);
  border: 1px solid var(--parchment-3);
  border-radius: 9px;
}

.table-row.open {
  background: var(--card);
  border-color: var(--edge);
}

.table-main {
  flex: 1;
  min-width: 0;
}

.table-title {
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
  min-width: 0;
}

.table-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.95rem;
}

.table-code {
  flex: 0 0 auto;
  font-family: ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.table-meta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8rem;
  color: var(--ink-soft);
}

.join-btn {
  flex: 0 0 auto;
  padding: 0.35rem 0.9rem;
  font-size: 0.85rem;
  white-space: nowrap;
}

.table-busy {
  flex: 0 0 auto;
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--ink-soft);
  background: var(--shade);
  border-radius: 999px;
}

.tables-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 1rem;
  font-size: 0.85rem;
  text-align: center;
  color: var(--ink-soft);
  border: 1.5px dashed var(--parchment-3);
  border-radius: 10px;
}

.empty-rune {
  font-size: 1.6rem;
  color: var(--gold-dark);
  opacity: 0.7;
}

.table-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 0.45rem;
  margin: 0.5rem 0 0.25rem;
  padding: 0.25rem 0.8rem;
  font-family: var(--font-title);
  font-weight: 700;
  background: var(--glass-2);
  border: 1px solid var(--parchment-3);
  border-radius: 999px;
}

.waiting .notice {
  margin: 0.5rem 0;
  text-align: left;
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
  color: var(--on-bg-soft);
  text-align: center;
}

.sep {
  opacity: 0.6;
}

.version {
  opacity: 0.75;
}

.link-btn {
  padding: 0;
  font: inherit;
  font-weight: 700;
  color: var(--gold-bright);
  background: none;
  border: none;
  text-decoration: underline;
  text-underline-offset: 3px;
  cursor: pointer;
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

/* niskie ekrany (np. 1366×768): mniejszy nagłówek, żeby cała lista bogów się zmieściła */
@media (max-height: 820px) {
  .start-screen {
    gap: 0.5rem;
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }

  .runes {
    display: none;
  }

  .title {
    font-size: clamp(2.5rem, 6vw, 3.25rem);
  }

  .divider {
    margin-top: 0.35rem;
  }

  .panel {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }

  .name-input {
    margin-bottom: 0.7rem;
    padding-top: 0.45rem;
    padding-bottom: 0.45rem;
  }

  .gods-header,
  .tables-header {
    margin-bottom: 0.4rem;
  }

  .gods-grid {
    gap: 0.35rem;
  }

  .god-option {
    padding-top: 0.35rem;
    padding-bottom: 0.3rem;
  }

  .god-detail {
    margin-top: 0.4rem;
  }
}

/* bardzo niskie okno (np. 1280×720 z paskami przeglądarki): bez podpisów łask na kafelkach */
@media (max-height: 680px) {
  .title {
    font-size: 2.4rem;
  }

  .divider {
    display: none;
  }

  .god-favor {
    display: none;
  }
}

/* węższy ekran: stoły pod wyborem bogów */
@media (max-width: 980px) {
  .lobby {
    grid-template-columns: minmax(0, 1fr);
  }

  .tables-col {
    min-height: 0;
    padding-left: 0;
    padding-top: 1rem;
    border-left: none;
    border-top: 1px solid var(--parchment-3);
  }

  .tables-inner {
    position: static;
  }

  .tables-list,
  .tables-empty {
    flex: 0 0 auto;
  }

  .tables-list {
    max-height: 22rem;
  }
}

@media (max-width: 600px) {
  .create-form {
    flex-wrap: wrap;
  }

  .create-btn {
    flex: 1 1 100%;
  }

  .panel {
    padding: 1.1rem;
  }

  .gods-grid {
    grid-template-columns: repeat(auto-fill, minmax(92px, 1fr));
  }

  .god-favor {
    display: none;
  }
}
</style>
