<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="stats-title">
      <button class="close" :aria-label="$t('help.close')" @click="$emit('close')">×</button>

      <div class="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          :class="{ active: tab === 'profile' }"
          :aria-selected="tab === 'profile'"
          :disabled="!viewLogin && !me"
          @click="openProfile(viewLogin || (me && me.login))"
        >
          {{ viewLogin && (!me || viewLogin.toLowerCase() !== me.login.toLowerCase()) ? $t('profile.playerTab', { name: viewLogin }) : $t('profile.myTab') }}
        </button>
        <button
          type="button"
          role="tab"
          :class="{ active: tab === 'ranking' }"
          :aria-selected="tab === 'ranking'"
          @click="openRanking"
        >
          {{ $t('ranking.title') }}
        </button>
      </div>

      <!-- profil gracza -->
      <section v-if="tab === 'profile'" class="profile">
        <p v-if="!profile" class="placeholder">{{ $t('profile.loading') }}</p>
        <p v-else-if="profile.missing" class="placeholder">{{ $t('profile.missing', { name: profile.login }) }}</p>
        <template v-else>
          <header class="profile-head">
            <div class="avatar" aria-hidden="true">{{ profile.login.charAt(0).toUpperCase() }}</div>
            <div class="who">
              <h2 id="stats-title">{{ profile.login }}</h2>
              <div class="since">{{ $t('profile.since', { date: day(profile.since) }) }}</div>
            </div>
            <div class="rating-box">
              <div class="rating-label">{{ $t('ranking.rating') }}</div>
              <div class="rating-value">{{ profile.rating }}</div>
              <div class="rating-sub">
                <template v-if="profile.position">{{ $t('profile.position', { n: profile.position }) }} · </template>
                <template v-else>{{ $t('profile.noRanked') }} · </template>
                {{ $t('profile.peak', { n: profile.peak }) }}
              </div>
            </div>
          </header>

          <div class="totals">
            <div class="total">
              <strong>{{ profile.totals.all.games }}</strong>
              <span>{{ $t('profile.games') }}</span>
            </div>
            <div class="total good">
              <strong>{{ profile.totals.all.wins }}</strong>
              <span>{{ $t('profile.wins') }}</span>
            </div>
            <div class="total bad">
              <strong>{{ profile.totals.all.losses }}</strong>
              <span>{{ $t('profile.losses') }}</span>
            </div>
            <div class="total">
              <strong>{{ percent(profile.totals.all) }}</strong>
              <span>{{ $t('profile.winRate') }}</span>
            </div>
          </div>
          <p class="breakdown">
            {{ $t('profile.ranked') }}: {{ record(profile.totals.ranked) }}
            <span class="sep">·</span>
            {{ $t('profile.normal') }}: {{ record(profile.totals.normal) }}
          </p>

          <div class="columns">
            <div class="col">
              <h3>{{ $t('profile.godsTitle') }}</h3>
              <p v-if="!profile.gods.length" class="placeholder small">{{ $t('profile.noGames') }}</p>
              <ul v-else class="gods">
                <li v-for="god in profile.gods" :key="god.name" class="god-row">
                  <img :src="icon(god.name)" alt="" class="god-icon" />
                  <span class="god-name">{{ $t('gods.name', god) }}</span>
                  <span class="god-games">{{ $t('profile.gamesShort', { n: god.games }) }}</span>
                  <span class="bar" :title="$t('profile.godRecord', { wins: god.wins, games: god.games })">
                    <span class="fill" :style="{ width: winShare(god) + '%' }"></span>
                  </span>
                  <span class="god-rate">{{ winShare(god) }}%</span>
                </li>
              </ul>
            </div>

            <div class="col">
              <h3>{{ $t('profile.historyTitle') }}</h3>
              <p v-if="!matches.length" class="placeholder small">{{ $t('profile.noGames') }}</p>
              <ul v-else class="history">
                <li v-for="match in matches" :key="match.id" class="match" :class="match.won ? 'won' : 'lost'">
                  <span class="result">{{ match.won ? $t('profile.win') : $t('profile.loss') }}</span>
                  <div class="match-main">
                    <div class="match-title">
                      <span>{{ $t('profile.vs') }}</span>
                      <button
                        v-if="match.opponent.account"
                        type="button"
                        class="player-link"
                        @click="openProfile(match.opponent.name)"
                      >{{ match.opponent.name }}</button>
                      <span v-else class="guest">{{ match.opponent.name }} <small>({{ $t('profile.guest') }})</small></span>
                      <span v-if="match.ranked" class="chip ranked">{{ $t('lobby.ranked') }}</span>
                      <span v-if="match.forfeit" class="chip">{{ $t('profile.forfeit') }}</span>
                    </div>
                    <div class="match-meta">
                      {{ when(match.at) }} · {{ $t('profile.rounds', { n: match.rounds }) }} · HP {{ match.hp }}:{{ match.opponent.hp }}
                      <span class="match-gods">
                        <img v-for="name in match.gods" :key="'me' + name" :src="icon(name)" :title="$t('gods.name', { name })" alt="" />
                        <span class="vs">/</span>
                        <img v-for="name in match.opponent.gods" :key="'op' + name" :src="icon(name)" :title="$t('gods.name', { name })" alt="" />
                      </span>
                    </div>
                  </div>
                  <span v-if="match.rating" class="delta" :class="{ up: delta(match) > 0 }">
                    {{ delta(match) > 0 ? '+' : '' }}{{ delta(match) }}
                  </span>
                </li>
              </ul>
              <button v-if="profile.history.more" type="button" class="btn btn-ghost more" @click="more">
                {{ $t('profile.more') }}
              </button>
            </div>
          </div>
        </template>
      </section>

      <!-- ranking -->
      <section v-else class="ranking">
        <h2 id="stats-title">{{ $t('ranking.title') }}</h2>
        <p class="lead">{{ $t('ranking.lead') }}</p>
        <p v-if="!ranking" class="placeholder">{{ $t('profile.loading') }}</p>
        <p v-else-if="!ranking.length" class="placeholder">{{ $t('ranking.empty') }}</p>
        <table v-else class="ranking-table">
          <thead>
            <tr>
              <th class="pos">#</th>
              <th>{{ $t('ranking.player') }}</th>
              <th class="num">{{ $t('ranking.rating') }}</th>
              <th class="num">{{ $t('ranking.record') }}</th>
              <th class="num">{{ $t('ranking.games') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in ranking" :key="row.login" :class="{ mine: me && row.login === me.login }">
              <td class="pos">{{ row.position }}</td>
              <td>
                <button type="button" class="player-link" @click="openProfile(row.login)">{{ row.login }}</button>
              </td>
              <td class="num strong">{{ row.rating }}</td>
              <td class="num">{{ row.wins }}–{{ row.losses }}</td>
              <td class="num">{{ row.games }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script>
import { account, loadMoreHistory, loadProfile, loadRanking } from '../account'
import { godIcon } from '../dice'
import { settings } from '../settings'

export default {
  name: 'StatsDialog',
  props: {
    // 'profile' albo 'ranking'
    initialTab: {
      type: String,
      default: 'profile'
    },
    // czyj profil; bez loginu własny
    login: {
      type: String,
      default: ''
    }
  },
  emits: ['close'],
  data() {
    return {
      tab: this.initialTab,
      viewLogin: this.login || ''
    }
  },
  computed: {
    me() {
      return account.user
    },
    profile() {
      return account.profile
    },
    ranking() {
      return account.ranking
    },
    matches() {
      return this.profile?.history?.matches || []
    },
    locale() {
      return settings.locale === 'en' ? 'en-GB' : 'pl-PL'
    }
  },
  mounted() {
    window.addEventListener('keydown', this.onKey)
    if (this.tab === 'ranking') this.openRanking()
    else this.openProfile(this.viewLogin || this.me?.login)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.onKey)
  },
  methods: {
    openProfile(login) {
      if (!login) return
      this.tab = 'profile'
      this.viewLogin = login
      loadProfile(login)
    },
    openRanking() {
      this.tab = 'ranking'
      loadRanking()
    },
    more() {
      loadMoreHistory()
    },
    icon(name) {
      return godIcon(name)
    },
    percent(totals) {
      return totals.games ? `${Math.round((totals.wins / totals.games) * 100)}%` : '–'
    },
    record(totals) {
      return this.$t('profile.record', totals)
    },
    winShare(god) {
      return god.games ? Math.round((god.wins / god.games) * 100) : 0
    },
    delta(match) {
      return match.rating.after - match.rating.before
    },
    day(seconds) {
      return new Date(seconds * 1000).toLocaleDateString(this.locale, { day: 'numeric', month: 'long', year: 'numeric' })
    },
    when(seconds) {
      return new Date(seconds * 1000).toLocaleString(this.locale, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
    },
    onKey(event) {
      if (event.key === 'Escape') this.$emit('close')
    }
  }
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
  overflow-y: auto;
  background: var(--overlay);
}

.dialog {
  position: relative;
  width: min(900px, 100%);
  box-sizing: border-box;
  padding: 1.1rem 1.5rem 1.3rem;
  color: var(--ink);
  background: linear-gradient(180deg, var(--panel-top) 0%, var(--parchment) 60%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}

.close {
  position: absolute;
  top: 0.6rem;
  right: 0.8rem;
  width: 32px;
  height: 32px;
  font-size: 1.4rem;
  line-height: 1;
  color: var(--ink-soft);
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
}

.close:hover {
  background: var(--shade);
}

.tabs {
  display: inline-flex;
  max-width: calc(100% - 2.5rem);
  margin-bottom: 1rem;
  border: 1px solid var(--edge);
  border-radius: 999px;
  overflow: hidden;
}

.tabs button {
  padding: 0.35rem 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--ink);
  background: var(--card);
  border: none;
  cursor: pointer;
}

.tabs button + button {
  border-left: 1px solid var(--edge);
}

.tabs button.active {
  color: var(--on-accent);
  background: var(--gold);
}

.tabs button:disabled {
  cursor: default;
  opacity: 0.55;
}

h2 {
  margin: 0;
  font-family: var(--font-title);
  font-size: 1.5rem;
  overflow-wrap: anywhere;
}

h3 {
  margin: 0 0 0.45rem;
  font-family: var(--font-title);
  font-size: 0.95rem;
  color: var(--gold-dark);
}

.lead {
  margin: 0.2rem 0 0.75rem;
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.placeholder {
  margin: 1.5rem 0;
  text-align: center;
  color: var(--ink-soft);
}

.placeholder.small {
  margin: 0.5rem 0;
  font-size: 0.85rem;
  text-align: left;
}

/* ---------- profil ---------- */

.profile-head {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.avatar {
  flex: 0 0 auto;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-title);
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--on-accent);
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
  border: 2px solid var(--gold-dark);
  border-radius: 50%;
}

.who {
  flex: 1;
  min-width: 0;
}

.since {
  font-size: 0.82rem;
  color: var(--ink-soft);
}

.rating-box {
  flex: 0 0 auto;
  text-align: right;
}

.rating-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-soft);
}

.rating-value {
  font-family: var(--font-title);
  font-size: 2rem;
  font-weight: 900;
  line-height: 1.05;
  color: var(--gold-dark);
}

.rating-sub {
  font-size: 0.78rem;
  color: var(--ink-soft);
}

.totals {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
}

.total {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0.25rem;
  background: var(--card);
  border: 1px solid var(--parchment-3);
  border-radius: 10px;
}

.total strong {
  font-family: var(--font-title);
  font-size: 1.5rem;
  line-height: 1.1;
}

.total span {
  font-size: 0.78rem;
  color: var(--ink-soft);
}

.total.good strong {
  color: var(--moss);
}

.total.bad strong {
  color: var(--blood);
}

.breakdown {
  margin: 0.5rem 0 0;
  font-size: 0.82rem;
  color: var(--ink-soft);
  text-align: center;
}

.sep {
  margin: 0 0.35rem;
  opacity: 0.6;
}

.columns {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  gap: 1.25rem;
  margin-top: 1rem;
}

.gods,
.history {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.history {
  max-height: 22rem;
  overflow-y: auto;
  padding-right: 0.15rem;
}

.god-row {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto 64px 2.6rem;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.85rem;
}

.god-icon {
  width: 22px;
  height: 22px;
  filter: var(--icon-filter);
}

.god-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 700;
}

.god-games {
  font-size: 0.75rem;
  color: var(--ink-soft);
  white-space: nowrap;
}

.bar {
  height: 6px;
  background: var(--parchment-3);
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--gold), var(--gold-bright));
}

.god-rate {
  font-size: 0.78rem;
  font-weight: 700;
  text-align: right;
}

.match {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.55rem;
  background: var(--card);
  border: 1px solid var(--parchment-3);
  border-left: 4px solid var(--blood);
  border-radius: 8px;
}

.match.won {
  border-left-color: var(--moss);
}

.result {
  flex: 0 0 4.6rem;
  font-family: var(--font-title);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--blood);
}

.match.won .result {
  color: var(--moss);
}

.match-main {
  flex: 1;
  min-width: 0;
}

.match-title {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.3rem;
  font-size: 0.88rem;
}

.guest small {
  color: var(--ink-soft);
}

.match-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.2rem 0.4rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.match-gods {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.match-gods img {
  width: 15px;
  height: 15px;
  filter: var(--icon-filter);
}

.match-gods .vs {
  margin: 0 2px;
}

.chip {
  padding: 0 0.45rem;
  font-size: 0.68rem;
  font-weight: 700;
  line-height: 1.5;
  color: var(--ink-soft);
  background: var(--shade);
  border-radius: 999px;
}

.chip.ranked {
  color: var(--on-accent);
  background: var(--gold);
}

.delta {
  flex: 0 0 auto;
  font-family: var(--font-title);
  font-weight: 700;
  color: var(--blood);
}

.delta.up {
  color: var(--moss);
}

.more {
  margin-top: 0.5rem;
  width: 100%;
}

.player-link {
  padding: 0;
  font: inherit;
  font-weight: 700;
  color: var(--ink);
  background: none;
  border: none;
  text-decoration: underline;
  text-decoration-color: var(--gold);
  text-underline-offset: 3px;
  cursor: pointer;
}

.player-link:hover {
  color: var(--gold-dark);
}

/* ---------- ranking ---------- */

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.ranking-table th {
  padding: 0.35rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-align: left;
  text-transform: uppercase;
  color: var(--ink-soft);
  border-bottom: 1.5px solid var(--edge);
}

.ranking-table td {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--parchment-3);
}

.ranking-table .num {
  text-align: right;
  white-space: nowrap;
}

.ranking-table .pos {
  width: 2.5rem;
  font-family: var(--font-title);
  font-weight: 700;
  color: var(--gold-dark);
}

.ranking-table .strong {
  font-weight: 800;
}

.ranking-table tr.mine td {
  background: var(--card-hi);
}

@media (max-width: 720px) {
  .columns {
    grid-template-columns: minmax(0, 1fr);
  }

  .totals {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .profile-head {
    flex-wrap: wrap;
  }

  .rating-box {
    width: 100%;
    text-align: left;
  }
}
</style>
