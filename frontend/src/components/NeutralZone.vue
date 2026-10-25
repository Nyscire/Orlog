<template>
  <div class="neutral-zone">
    <div class="stage-indicator">
      <div class="stage-badge" :class="stageClass">
        {{ stageText }}<span v-if="round && stage !== 'waiting'"> · Runda {{ round }}</span>
      </div>
      <div class="stage-right">
        <div class="turn-indicator" v-if="activePlayer">
          <template v-if="activePlayer === player.name">Twoja tura</template>
          <template v-else>Ruch: <span class="active-player">{{ activePlayer }}</span></template>
        </div>
        <template v-if="!confirmLeave">
          <button class="help-btn" @click="$emit('help')">Jak grać?</button>
          <button class="help-btn" @click="confirmLeave = true">Opuść grę</button>
        </template>
        <span v-else class="leave-confirm">
          Zakończyć partię dla obu graczy?
          <button class="help-btn danger" @click="$emit('leave')">Tak, wyjdź</button>
          <button class="help-btn" @click="confirmLeave = false">Nie</button>
        </span>
      </div>
    </div>

    <!-- Central Battle Area -->
    <div class="battle-arena">
      <div class="player-battle-side">
        <div class="saved-dice-area">
          <h4>Twoje odłożone kości</h4>
          <DiceDisplay
            :dice="player.saved_dice || []"
            :selectable="false"
            compact
          />
          <div class="dice-summary">{{ summary(player.saved_dice) || 'Jeszcze nic nie odłożono' }}</div>
        </div>
        <div class="chosen-god-area" v-if="player.chosen_god">
          <GodsNeutralDisplay :god="player.chosen_god" tooltip-align="left" />
        </div>
      </div>

      <div class="vs-divider">
        <div class="vs-circle">VS</div>
      </div>

      <div class="opponent-battle-side">
        <div class="saved-dice-area">
          <h4>Odłożone kości przeciwnika</h4>
          <DiceDisplay
            :dice="opponent.saved_dice || []"
            :selectable="false"
            compact
          />
          <div class="dice-summary">{{ summary(opponent.saved_dice) || 'Jeszcze nic nie odłożono' }}</div>
        </div>
        <div class="chosen-god-area" v-if="opponent.chosen_god">
          <GodsNeutralDisplay :god="opponent.chosen_god" tooltip-align="right" />
        </div>
      </div>
    </div>

    <EventLog :entries="log" />

    <!-- Stage Instructions -->
    <div class="instructions">
      <div v-if="stage === 'finished'" class="instruction-text game-over">
        <span>{{ winner === player.name ? 'Wygrałeś!' : `Wygrywa ${winner}` }}</span>
        <button class="btn btn-gold new-game-button" @click="$emit('new-game')">Nowa partia</button>
      </div>
      <div v-else-if="instruction" class="instruction-text">{{ instruction }}</div>
    </div>
  </div>
</template>

<script>
import DiceDisplay from './DiceDisplay.vue'
import GodsNeutralDisplay from './GodsNeutralDisplay.vue'
import EventLog from './EventLog.vue'
import { diceSummary } from '../dice'

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
    }
  },
  emits: ['new-game', 'help', 'leave'],
  data() {
    return {
      confirmLeave: false
    }
  },
  computed: {
    // podpowiedź, co teraz zrobić
    instruction() {
      const mine = this.activePlayer === this.player.name
      if (this.stage === 'waiting') return 'Czekamy na drugiego gracza…'
      if (this.stage === 'dice') {
        if (!mine) return `${this.activePlayer} rzuca kośćmi…`
        if (this.player.rzuty === 1) return 'Ostatni rzut: wszystkie wylosowane kości zostaną zachowane.'
        return 'Kliknij kości, które chcesz zatrzymać, i potwierdź. Pozostałe rzucisz ponownie.'
      }
      if (this.stage === 'gods') {
        if (!mine) return `${this.activePlayer} wybiera łaskę boga…`
        const mana = this.player.mana_available ?? this.player.Mana ?? 0
        return `Wybierz poziom łaski i kliknij „Wybierz” albo pomiń łaskę. Masz do wydania ${mana} many.`
      }
      return ''
    },
    stageText() {
      const stages = {
        'waiting': 'Oczekiwanie na graczy',
        'dice': 'Faza Kości',
        'gods': 'Wybór Bogów',
        'battle': 'Walka!',
        'finished': 'Koniec Gry'
      }
      return stages[this.stage] || 'Nieznana faza'
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
  },
  methods: {
    summary(dice) {
      return diceSummary(dice)
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
  background: radial-gradient(ellipse at 50% 40%, #faf3e2 0%, var(--parchment) 45%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 12px;
  box-shadow: inset 0 0 30px rgba(140, 106, 44, 0.18), 0 6px 20px rgba(0, 0, 0, 0.35);
}

.stage-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.stage-badge {
  padding: 0.3rem 0.9rem;
  border-radius: 999px;
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  color: var(--parchment);
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
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid var(--edge);
  border-radius: 999px;
  cursor: pointer;
}

.help-btn:hover {
  background: rgba(255, 255, 255, 0.85);
}

.help-btn.danger {
  color: var(--parchment);
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
  background: rgba(255, 255, 255, 0.4);
  padding: 0.4rem 0.75rem;
  border: 1px dashed var(--edge);
  border-radius: 12px;
  box-sizing: border-box;
  width: 360px;
  max-width: 100%;
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
  min-height: 4.5rem;
}

.instructions {
  background: rgba(43, 29, 18, 0.06);
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