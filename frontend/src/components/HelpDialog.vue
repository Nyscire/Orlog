<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="help-title">
      <button class="close" :aria-label="$t('help.close')" @click="$emit('close')">×</button>
      <h2 id="help-title">{{ $t('help.title') }}</h2>
      <p class="lead">{{ $t('help.lead') }}</p>

      <h3>{{ $t('help.roundTitle') }}</h3>
      <ol class="steps">
        <li v-for="(step, i) in $t('help.steps')" :key="i">
          <strong>{{ step.title }}</strong> {{ step.text }}
        </li>
      </ol>

      <h3>{{ $t('help.diceTitle') }}</h3>
      <ul class="legend">
        <li v-for="face in faces" :key="face">
          <span class="tile"><img :src="`/img/icons/${face}.svg`" alt="" /></span>
          <span class="legend-text"><strong>{{ $t(`dice.${face}.name`) }}</strong> {{ $t(`dice.${face}.desc`) }}</span>
        </li>
        <li>
          <span class="tile gold"><img src="/img/icons/axe.svg" alt="" /><i class="coin"></i></span>
          <span class="legend-text"><strong>{{ $t('dice.coinName') }}</strong> {{ $t('dice.coinLegend') }}</span>
        </li>
      </ul>

      <h3>{{ $t('help.attackTitle') }}</h3>
      <p>{{ $t('help.attackText') }}</p>

      <h3>{{ $t('help.manaTitle') }}</h3>
      <p>{{ $t('help.manaText') }}</p>

      <div class="actions">
        <button class="btn btn-gold" @click="$emit('close')">{{ $t('help.ok') }}</button>
      </div>
    </div>
  </div>
</template>

<script>
import { FACE_ORDER } from '../dice'

export default {
  name: 'HelpDialog',
  emits: ['close'],
  computed: {
    faces() {
      return FACE_ORDER
    }
  },
  mounted() {
    window.addEventListener('keydown', this.onKey)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.onKey)
  },
  methods: {
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
  width: min(640px, 100%);
  box-sizing: border-box;
  padding: 1.5rem 1.75rem 1.25rem;
  color: var(--ink);
  background: linear-gradient(180deg, var(--panel-top) 0%, var(--parchment) 60%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
  line-height: 1.45;
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

h2 {
  margin: 0 2rem 0.5rem 0;
  font-family: var(--font-title);
  font-size: 1.5rem;
}

h3 {
  margin: 1.1rem 0 0.4rem;
  font-family: var(--font-title);
  font-size: 1rem;
  color: var(--gold-dark);
}

p {
  margin: 0.3rem 0;
  font-size: 0.92rem;
}

.lead {
  font-size: 1rem;
}

.steps {
  margin: 0.3rem 0;
  padding-left: 1.3rem;
  font-size: 0.92rem;
}

.steps li + li {
  margin-top: 0.35rem;
}

.legend {
  list-style: none;
  margin: 0.3rem 0;
  padding: 0;
  display: grid;
  gap: 0.45rem;
}

.legend li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
}

.legend-text strong {
  margin-right: 0.25rem;
}

.tile {
  position: relative;
  flex: 0 0 auto;
  width: 38px;
  height: 38px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: linear-gradient(145deg, var(--die-1) 0%, var(--die-2) 60%, var(--die-3) 100%);
  border: 1px solid var(--die-edge);
}

.tile img {
  width: 24px;
  height: 24px;
}

.tile.gold {
  border: 2px solid var(--gold);
}

.coin {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, var(--coin-light), var(--gold) 55%, var(--gold-dark));
  border: 1px solid var(--gold-dark);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.1rem;
}

@media (max-width: 600px) {
  .dialog {
    padding: 1.1rem;
  }
}
</style>
