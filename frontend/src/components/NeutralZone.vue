<template>
  <div class="neutral-zone">
    <div class="stage-indicator">
      <div class="stage-left">
        <div class="stage-badge" :class="stageClass">
          {{ stageText }}<span v-if="round && stage !== 'waiting'"> · {{ $t('neutral.round', { n: round }) }}</span>
        </div>
        <span v-if="table" class="table-label" :title="$t('neutral.tableCode', { code: table.id })">
          {{ table.name || $t('lobby.defaultName', { host: table.host }) }} <span class="table-code">#{{ table.id }}</span>
        </span>
      </div>
      <div class="stage-right">
        <div class="turn-indicator" v-if="activePlayer">
          <template v-if="activePlayer === player.name">{{ $t('neutral.yourTurn') }}</template>
          <template v-else>{{ $t('neutral.turnOf') }} <span class="active-player">{{ activePlayer }}</span></template>
        </div>
        <template v-if="!confirmLeave">
          <button class="help-btn" @click="$emit('help')">{{ $t('neutral.howToPlay') }}</button>
          <button class="help-btn" @click="confirmLeave = true">{{ $t('neutral.leave') }}</button>
          <button
            class="help-btn icon-btn"
            :title="$t('neutral.settings')"
            :aria-label="$t('neutral.settings')"
            @click="$emit('settings')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
              <path fill="currentColor" d="M19.4 13a7.6 7.6 0 0 0 0-2l2.1-1.6-2-3.5-2.5 1a7.4 7.4 0 0 0-1.7-1L15 3.3h-4l-.4 2.6a7.4 7.4 0 0 0-1.7 1l-2.5-1-2 3.5L6.6 11a7.6 7.6 0 0 0 0 2l-2.1 1.6 2 3.5 2.5-1a7.4 7.4 0 0 0 1.7 1l.4 2.6h4l.4-2.6a7.4 7.4 0 0 0 1.7-1l2.5 1 2-3.5zM13 15.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7z" transform="translate(-1 0)"/>
            </svg>
          </button>
        </template>
        <span v-else class="leave-confirm">
          {{ $t('neutral.leaveConfirm') }}
          <button class="help-btn danger" @click="$emit('leave')">{{ $t('neutral.leaveYes') }}</button>
          <button class="help-btn" @click="confirmLeave = false">{{ $t('neutral.no') }}</button>
        </span>
      </div>
    </div>

    <div class="battle-arena">
      <div class="player-battle-side">
        <div class="saved-dice-area" :class="{ targetable: targetMode === 'any_dice' }">
          <h4>{{ $t('neutral.yourSaved') }}</h4>
          <DiceDisplay
            :dice="player.saved_dice || []"
            :selectable="targetMode === 'any_dice'"
            :selected-indexes="targetMode ? pick.own : []"
            compact
            @toggle-selection="$emit('toggle-target', { side: 'own', index: $event })"
          />
          <div class="dice-summary">{{ $t('dice.summary', player.saved_dice || []) || $t('neutral.nothingSaved') }}</div>
        </div>
        <div class="chosen-god-area" v-if="player.chosen_god">
          <GodsNeutralDisplay :god="player.chosen_god" :choice="player.chosen_choice" tooltip-align="left" />
        </div>
      </div>

      <div class="vs-divider">
        <div class="vs-circle">VS</div>
      </div>

      <div class="opponent-battle-side">
        <div class="saved-dice-area" :class="{ targetable: !!targetMode }">
          <h4>{{ $t('neutral.opponentSaved') }}</h4>
          <DiceDisplay
            :dice="opponent.saved_dice || []"
            :selectable="!!targetMode"
            :selected-indexes="targetMode ? pick.opponent : []"
            compact
            @toggle-selection="$emit('toggle-target', { side: 'opponent', index: $event })"
          />
          <div class="dice-summary">{{ $t('dice.summary', opponent.saved_dice || []) || $t('neutral.nothingSaved') }}</div>
        </div>
        <div class="chosen-god-area" v-if="opponent.chosen_god">
          <GodsNeutralDisplay :god="opponent.chosen_god" :choice="opponent.chosen_choice" tooltip-align="right" />
        </div>
      </div>
    </div>

    <EventLog :entries="log" />

    <div class="instructions">
      <div v-if="stage === 'finished'" class="instruction-text game-over">
        <span>{{ winner === player.name ? $t('neutral.youWin') : $t('neutral.winnerIs', { name: winner }) }}</span>
        <button class="btn btn-gold new-game-button" @click="$emit('new-game')">{{ $t('neutral.newGame') }}</button>
      </div>
      <div v-else-if="instruction" class="instruction-text">{{ instruction }}</div>
    </div>
  </div>
</template>

<script>
import DiceDisplay from './DiceDisplay.vue'
import GodsNeutralDisplay from './GodsNeutralDisplay.vue'
import EventLog from './EventLog.vue'

export default {
  name: 'NeutralZone',
  components: {
    DiceDisplay,
    GodsNeutralDisplay,
    EventLog
  },
  props: {
    stage: {
      type: String,
      default: 'waiting'
    },
    activePlayer: String,
    winner: String,
    round: Number,
    // stół, przy którym toczy się partia: { id, name, host }
    table: {
      type: Object,
      default: null
    },
    log: {
      type: Array,
      default: () => []
    },
    player: {
      type: Object,
      default: () => ({})
    },
    opponent: {
      type: Object,
      default: () => ({})
    },
    // łaska wybierana w tej chwili; Frigg i Loki wskazują kości na stole
    pick: {
      type: Object,
      default: null
    }
  },
  emits: ['new-game', 'help', 'leave', 'settings', 'toggle-target'],
  data() {
    return {
      confirmLeave: false
    }
  },
  computed: {
    // 'opponent_dice' (Loki), 'any_dice' (Frigg) albo null
    targetMode() {
      const needs = this.pick?.level ? this.pick.needs : null
      return needs === 'opponent_dice' || needs === 'any_dice' ? needs : null
    },
    // podpowiedź, co teraz zrobić
    instruction() {
      const mine = this.activePlayer === this.player.name
      if (this.stage === 'waiting') return this.$t('neutral.hint.waiting')
      if (this.stage === 'dice') {
        if (!mine) return this.$t('neutral.hint.opponentRolling', { name: this.activePlayer })
        if (this.player.rzuty === 1) return this.$t('neutral.hint.lastThrow')
        return this.$t('neutral.hint.pickDice')
      }
      if (this.stage === 'gods') {
        if (!mine) return this.$t('neutral.hint.opponentChoosing', { name: this.activePlayer })
        if (this.targetMode) {
          return this.$t('gods.pickTargetsHint', { god: this.pick.god, max: this.pick.max, any: this.targetMode === 'any_dice' })
        }
        return this.$t('neutral.hint.pickGod', { mana: this.player.mana_available ?? this.player.Mana ?? 0 })
      }
      return ''
    },
    stageText() {
      return this.$t(`stage.${this.stage}`) === `stage.${this.stage}` ? this.$t('stage.unknown') : this.$t(`stage.${this.stage}`)
    },
    stageClass() {
      return {
        'stage-waiting': this.stage === 'waiting',
        'stage-dice': this.stage === 'dice',
        'stage-gods': this.stage === 'gods',
        'stage-battle': this.stage === 'battle',
        'stage-finished': this.stage === 'finished'
      }
    }
  }
}
</script>

<style scoped>
/* stół do gry: jasny pergamin z ciemniejszymi brzegami */
.neutral-zone {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.45rem 1rem;
  background: radial-gradient(ellipse at 50% 40%, var(--panel-top) 0%, var(--parchment) 45%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 12px;
  box-shadow: inset 0 0 30px rgba(var(--accent-rgb), 0.18), 0 6px 20px rgba(0, 0, 0, 0.35);
}

.stage-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.stage-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 0;
}

.stage-left .stage-badge {
  flex: 0 0 auto;
  white-space: nowrap;
}

.table-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-title);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--ink-soft);
}

.table-code {
  font-family: ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 0.72rem;
  letter-spacing: 0.05em;
}

.stage-badge {
  padding: 0.3rem 0.9rem;
  border-radius: 999px;
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  color: var(--on-strong);
  border: 1px solid rgba(0, 0, 0, 0.25);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.stage-waiting {
  background: var(--ink-soft);
}

.stage-dice {
  background: var(--rune);
}

.stage-gods {
  background: var(--violet);
}

.stage-battle {
  background: var(--blood);
  animation: battlePulse 2s ease-in-out infinite;
}

.stage-finished {
  background: var(--moss);
}

@keyframes battlePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.stage-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.help-btn {
  padding: 0.2rem 0.7rem;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--ink);
  background: var(--glass-2);
  border: 1px solid var(--edge);
  border-radius: 999px;
  cursor: pointer;
}

.help-btn:hover {
  background: var(--glass-3);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.45rem;
}

.help-btn.danger {
  color: var(--on-strong);
  background: var(--blood);
  border-color: rgba(0, 0, 0, 0.3);
}

.leave-confirm {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.dice-summary {
  margin-top: 0.25rem;
  font-size: 0.72rem;
  line-height: 1.3;
  text-align: center;
  color: var(--ink-soft);
}

.turn-indicator {
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--ink);
}

.active-player {
  color: var(--blood);
}

/* [bóg][kości]  VS  [kości][bóg] */
.battle-arena {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.player-battle-side,
.opponent-battle-side {
  flex: 1;
  min-width: 0;   /* na węższym ekranie pole z kośćmi się zwęża, zamiast wychodzić poza ekran */
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.player-battle-side {
  flex-direction: row-reverse;
}

.saved-dice-area {
  background: var(--glass);
  padding: 0.4rem 0.75rem;
  border: 1px dashed var(--edge);
  border-radius: 12px;
  box-sizing: border-box;
  width: 360px;
  max-width: 100%;
}

/* Frigg i Loki: tu klika się kości */
.saved-dice-area.targetable {
  border: 1.5px solid var(--gold);
  background: rgba(var(--accent-rgb), 0.12);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.2);
}

.saved-dice-area h4 {
  margin: 0 0 0.35rem 0;
  text-align: center;
  font-family: var(--font-title);
  color: var(--ink-soft);
  font-size: 0.8rem;
}

.chosen-god-area {
  padding: 0.25rem;
}

.vs-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 56px;
}

/* nieruchomy znak VS, żeby dało się go przeczytać */
.vs-circle {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 35%, var(--wood-600), var(--wood-900));
  color: var(--gold-bright);
  border: 2px solid var(--gold);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-title);
  font-weight: 900;
  font-size: 0.95rem;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.35);
}

/* dziennik zajmuje wolne miejsce w środku, a jak wpisów jest więcej, przewija się w środku */
.event-log {
  flex: 1 1 0;
  min-height: 3.75rem;
}

.instructions {
  background: var(--shade);
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  text-align: center;
}

.instruction-text {
  font-size: 0.9rem;
  color: var(--ink);
  font-weight: 500;
}

.game-over {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-family: var(--font-title);
  font-size: 1.2rem;
  font-weight: 900;
  color: var(--gold-dark);
}

/* wąskie ekrany: strony jedna pod drugą */
@media (max-width: 900px) {
  .battle-arena {
    flex-direction: column;
    gap: 0.5rem;
  }

  .player-battle-side,
  .opponent-battle-side {
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }

  .vs-divider {
    flex-basis: auto;
  }
}
</style>