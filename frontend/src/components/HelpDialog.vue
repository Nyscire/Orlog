<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="help-title">
      <button class="close" aria-label="Zamknij" @click="$emit('close')">×</button>
      <h2 id="help-title">Jak grać w Orlog</h2>
      <p class="lead">
        Wygrywa ten, kto pierwszy sprowadzi życie przeciwnika do zera. Każdy zaczyna z 21 HP.
      </p>

      <h3>Przebieg rundy</h3>
      <ol class="steps">
        <li>
          <strong>Rzuty kośćmi.</strong> Gracze rzucają na zmianę sześcioma kośćmi. Po każdym rzucie
          zaznaczasz kości, które chcesz zatrzymać, a resztę rzucasz ponownie. Masz 3 rzuty,
          w ostatnim zostają wszystkie kości.
        </li>
        <li>
          <strong>Łaski bogów.</strong> Każdy może kupić łaskę jednego ze swoich bogów albo ją pominąć.
          Łaska kosztuje manę, a wyższy poziom daje silniejszy efekt.
        </li>
        <li>
          <strong>Walka.</strong> Mana z kości trafia do puli, działają łaski, a potem atakuje gracz,
          który zaczynał rundę, i po nim drugi. W następnej rundzie zaczyna drugi gracz.
        </li>
      </ol>

      <h3>Kości</h3>
      <ul class="legend">
        <li v-for="face in faces" :key="face">
          <span class="tile"><img :src="`/img/icons/${face}.svg`" alt="" /></span>
          <span class="legend-text"><strong>{{ info[face].name }}</strong> {{ info[face].desc }}</span>
        </li>
        <li>
          <span class="tile gold"><img src="/img/icons/axe.svg" alt="" /><i class="coin"></i></span>
          <span class="legend-text"><strong>Złota obwódka</strong> Kość daje dodatkowo 1 manę, niezależnie od symbolu.</span>
        </li>
      </ul>

      <h3>Jak liczy się atak</h3>
      <p>
        Każda strzała zadaje 1 obrażenie, chyba że zablokuje ją tarcza. Każdy topór zadaje 1 obrażenie,
        chyba że zablokuje go hełm. Na przykład 3 strzały na 1 tarczę to 2 obrażenia.
      </p>

      <h3>Mana i bogowie</h3>
      <p>
        Niewydana mana zostaje na kolejne rundy. Przed grą wybierasz do 3 bogów. Po najechaniu na kartę
        boga zobaczysz, co robi, a po wybraniu poziomu: jego efekt i koszt.
      </p>

      <div class="actions">
        <button class="btn btn-gold" @click="$emit('close')">Rozumiem</button>
      </div>
    </div>
  </div>
</template>

<script>
import { DICE_INFO, FACE_ORDER } from '../dice'

export default {
  name: 'HelpDialog',
  emits: ['close'],
  computed: {
    info() {
      return DICE_INFO
    },
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
  background: rgba(15, 10, 6, 0.7);
}

.dialog {
  position: relative;
  width: min(640px, 100%);
  box-sizing: border-box;
  padding: 1.5rem 1.75rem 1.25rem;
  color: var(--ink);
  background: linear-gradient(180deg, #f8f0de 0%, var(--parchment) 60%, var(--parchment-2) 100%);
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
  background: rgba(43, 29, 18, 0.08);
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
  background: linear-gradient(145deg, #fdf6e6 0%, #efe0bf 60%, #e2cc9e 100%);
  border: 1px solid #b0915c;
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
  background: radial-gradient(circle at 35% 35%, #fff1bf, var(--gold) 55%, var(--gold-dark));
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
