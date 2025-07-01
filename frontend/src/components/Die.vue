<template>
  <div
    class="die"
    :class="dieClasses"
    @click="handleClick"
    @mouseenter="handleHover"
    @mouseleave="handleLeave"
  >
    <!-- Main die content -->
    <div class="die-content">
      <img 
        :src="`/img/icons/${die.stat}.svg`" 
        :alt="die.stat" 
        class="die-icon"
      />
      
      <!-- Selection indicator -->
      <div v-if="selected" class="selection-indicator">
        <span class="checkmark">✓</span>
      </div>
      
      <!-- Mana indicator -->
      <div v-if="die.gives_mana" class="mana-indicator">
        <span class="mana-icon">🔮</span>
      </div>
      
      <!-- Hover tooltip -->
      <transition name="tooltip-fade">
        <div v-if="showTooltip" class="die-tooltip">
          <div class="tooltip-content">
            <strong>{{ formatStatName(die.stat) }}</strong>
            <div v-if="die.gives_mana" class="tooltip-mana">Daje Manę</div>
          </div>
        </div>
      </transition>
    </div>
    
    <!-- Ripple effect -->
    <div v-if="ripple" class="ripple-effect" :style="rippleStyle"></div>
  </div>
</template>

<script>
export default {
  name: 'Die',
  props: {
    die: {
      type: Object,
      required: true
    },
    selected: Boolean,
    selectable: Boolean
  },
  data() {
    return {
      showTooltip: false,
      ripple: false,
      rippleStyle: {}
    }
  },
  computed: {
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
      if (this.selectable || this.die.gives_mana) {
        this.showTooltip = true
      }
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
    },
    
    formatStatName(stat) {
      const statNames = {
        'strength': 'Siła',
        'agility': 'Zręczność',
        'intelligence': 'Inteligencja',
        'defense': 'Obrona',
        'magic': 'Magia',
        'luck': 'Szczęście'
      }
      return statNames[stat] || stat.charAt(0).toUpperCase() + stat.slice(1)
    }
  }
}
</script>

<style scoped>
.die {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.die-content {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.die-icon {
  width: 32px;
  height: 32px;
  transition: transform 0.3s ease;
  z-index: 2;
}

/* Interactive states */
.die.selectable {
  cursor: pointer;
}

.die.selectable:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  border-color: #007bff;
}

.die.selectable:hover .die-icon {
  transform: scale(1.1);
}

.die.interactive:active {
  transform: translateY(0) scale(1.02);
}

/* Selection state */
.die.selected {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
  animation: selectedPulse 2s ease-in-out infinite;
}

@keyframes selectedPulse {
  0%, 100% { 
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
  }
  50% { 
    box-shadow: 0 0 0 6px rgba(33, 150, 243, 0.2);
  }
}

.selection-indicator {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #4caf50, #388e3c);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.checkmark {
  color: white;
  font-size: 10px;
  font-weight: bold;
}

/* Mana state */
.die.mana {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  border: 2px dashed #4caf50;
  position: relative;
}

.die.mana::before {
  content: '';
  position: absolute;
  inset: 2px;
  border-radius: 8px;
  background: linear-gradient(135deg, transparent, rgba(76, 175, 80, 0.1));
  animation: manaShimmer 3s ease-in-out infinite;
}

@keyframes manaShimmer {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.mana-indicator {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #9c27b0, #7b1fa2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  border: 2px solid white;
}

.mana-icon {
  font-size: 10px;
}

/* Tooltip */
.die-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  z-index: 10;
}

.tooltip-content {
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.9);
}

.tooltip-mana {
  font-size: 10px;
  opacity: 0.8;
  margin-top: 2px;
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
  background: rgba(33, 150, 243, 0.3);
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

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .die,
  .die-icon,
  .selection-indicator,
  .tooltip-content {
    transition: none;
  }
  
  .die.selected {
    animation: none;
  }
  
  .ripple-effect {
    display: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .die {
    border-width: 3px;
  }
  
  .die.selected {
    border-color: #000;
    background: #fff;
  }
  
  .die.mana {
    border-color:#007bff;
    background: #388e3c;
  }
}
  </style>