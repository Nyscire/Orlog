<template>
  <div
    class="die"
    :class="dieClasses"
    :aria-label="ariaLabel"
    @click="handleClick"
    @mouseenter="handleHover"
    @mouseleave="handleLeave"
  >
    <div class="die-content">
      <img :src="`/img/icons/${die.stat}.svg`" alt="" class="die-icon" />

      <div v-if="selected" class="selection-indicator">
        <span class="checkmark">✓</span>
      </div>

      <div v-if="die.gives_mana" class="mana-indicator"></div>

      <div v-if="ripple" class="ripple-effect" :style="rippleStyle"></div>
    </div>

    <!-- podpowiedź jest poza .die-content, żeby nie ucinało jej zaokrąglenie kafelka -->
    <transition name="tooltip-fade">
      <div v-if="showTooltip" class="die-tooltip" :class="`place-${tooltipPlacement}`">
        <div class="tooltip-content">
          <strong>{{ info.name }}</strong>
          <div class="tooltip-desc">{{ info.desc }}</div>
          <div v-if="die.gives_mana" class="tooltip-mana">{{ manaBorderDesc }}</div>
        </div>
      </div>
    </transition>

    <span v-if="label" class="die-label">{{ info.name }}</span>
  </div>
</template>

<script>
import { DICE_INFO, MANA_BORDER_DESC } from '../dice'

export default {
  name: 'Die',
  props: {
    die: {
      type: Object,
      required: true
    },
    selected: Boolean,
    selectable: Boolean,
    // podpis pod kafelkiem (dla kości, które gracz właśnie wybiera)
    label: Boolean,
    tooltipPlacement: {
      type: String,
      default: 'above'
    }
  },
  // Bez tej deklaracji Vue podpina @click rodzica także pod zwykłe kliknięcie w element,
  // przez co zaznaczenie kości przełączało się dwa razy i od razu znikało.
  emits: ['click'],
  data() {
    return {
      showTooltip: false,
      ripple: false,
      rippleStyle: {}
    }
  },
  computed: {
    info() {
      return DICE_INFO[this.die.stat] || { name: this.die.stat, desc: '' }
    },
    manaBorderDesc() {
      return MANA_BORDER_DESC
    },
    ariaLabel() {
      return this.info.name + (this.die.gives_mana ? ', daje dodatkowo 1 manę' : '')
    },
    dieClasses() {
      return {
        'selected': this.selected,
        'mana': this.die.gives_mana,
        'selectable': this.selectable,
        'interactive': this.selectable
      }
    }
  },
  methods: {
    handleClick(event) {
      if (!this.selectable) return
      
      this.createRipple(event)
      this.$emit('click')
    },
    
    handleHover() {
      this.showTooltip = true
    },
    
    handleLeave() {
      this.showTooltip = false
    },
    
    createRipple(event) {
      const rect = this.$el.getBoundingClientRect()
      const size = Math.max(rect.width, rect.height)
      const x = event.clientX - rect.left - size / 2
      const y = event.clientY - rect.top - size / 2
      
      this.rippleStyle = {
        width: size + 'px',
        height: size + 'px',
        left: x + 'px',
        top: y + 'px'
      }
      
      this.ripple = true
      
      setTimeout(() => {
        this.ripple = false
      }, 600)
    }
  }
}
</script>

<style scoped>
/* kość jak kawałek kości/drewna: jasny kafelek, ciemny symbol */
.die {
  position: relative;
  /* rozmiar ustawia DiceDisplay (--die-size), domyślnie 56px */
  width: var(--die-size, 56px);
  height: var(--die-size, 56px);
  flex: 0 0 auto;
  box-sizing: border-box;
  border-radius: calc(var(--die-size, 56px) * 0.2);
  background: linear-gradient(145deg, #fdf6e6 0%, #efe0bf 60%, #e2cc9e 100%);
  border: 1px solid #b0915c;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: default;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8), inset 0 -2px 0 rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.3);
}

.die-content {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: inherit;
}

.die-label {
  position: absolute;
  top: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--ink-soft);
  white-space: nowrap;
  pointer-events: none;
}

.die-icon {
  width: calc(var(--die-size, 56px) * 0.6);
  height: calc(var(--die-size, 56px) * 0.6);
  transition: transform 0.2s ease;
  z-index: 2;
}

.die.selectable {
  cursor: pointer;
}

.die.selectable:hover {
  transform: translateY(-2px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8), 0 6px 12px rgba(0, 0, 0, 0.35);
}

.die.interactive:active {
  transform: translateY(0);
}

/* zaznaczona kość: uniesiona, ze złotą obwódką */
.die.selected {
  transform: translateY(-3px);
  border-color: var(--gold-dark);
  box-shadow: 0 0 0 3px var(--gold), 0 0 0 4px var(--gold-dark), 0 6px 14px rgba(0, 0, 0, 0.35);
}

.selection-indicator {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  background: var(--ink);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
}

.checkmark {
  color: var(--gold-bright);
  font-size: 10px;
  font-weight: bold;
}

/* kość dająca manę: złota obwódka i złota moneta w rogu */
.die.mana {
  border: 2px solid var(--gold);
}

.mana-indicator {
  position: absolute;
  top: 3px;
  right: 3px;
  width: calc(var(--die-size, 56px) * 0.22);
  height: calc(var(--die-size, 56px) * 0.22);
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff1bf, var(--gold) 55%, var(--gold-dark));
  border: 1px solid var(--gold-dark);
  z-index: 3;
}

/* Tooltip */
.die-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  z-index: 30;
  pointer-events: none;
}

.die-tooltip.place-below {
  bottom: auto;
  top: 100%;
  margin: 8px 0 0;
}

.tooltip-content {
  width: 190px;
  background: rgba(28, 19, 12, 0.96);
  color: var(--parchment);
  padding: 7px 10px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.35;
  text-align: left;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}

.tooltip-desc {
  margin-top: 2px;
}

.tooltip-mana {
  margin-top: 4px;
  color: var(--gold-bright);
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: all 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}

/* Ripple effect */
.ripple-effect {
  position: absolute;
  border-radius: 50%;
  background: rgba(201, 162, 76, 0.35);
  transform: scale(0);
  animation: ripple 0.6s linear;
  pointer-events: none;
}

@keyframes ripple {
  to {
    transform: scale(2);
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .die,
  .die-icon {
    transition: none;
  }

  .ripple-effect {
    display: none;
  }
}
</style>