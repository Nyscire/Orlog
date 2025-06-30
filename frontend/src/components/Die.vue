<template>
  <div
    class="die"
    :class="{
      selected: selected,
      mana: die.gives_mana,
      selectable: selectable
    }"
    @click="handleClick"
  >
    <div class="die-inner">
      <div class="die-face">
        <img :src="`/img/icons/${die.stat}.svg`" :alt="die.stat" />
      </div>
      
      <!-- Selection indicator -->
      <div v-if="selected" class="selection-indicator">
        <span class="check-mark">✓</span>
      </div>
      
      <!-- Mana indicator -->
      <div v-if="die.gives_mana" class="mana-indicator">
        <span class="mana-icon">🪄</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    die: {
      type: Object,
      required: true
    },
    selected: Boolean,
    selectable: Boolean
  },
  methods: {
    handleClick() {
      if (this.selectable) {
        this.$emit('click')
      }
    }
  }
}
</script>



<style scoped>
.die {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  cursor: default;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  perspective: 1000px;
}

.die-inner {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
}

.die-face {
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #ffffff, #f0f0f0);
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 
    0 4px 8px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  position: relative;
  overflow: hidden;
}

.die-face::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.4) 0%, 
    rgba(255, 255, 255, 0.1) 50%, 
    rgba(0, 0, 0, 0.05) 100%);
  pointer-events: none;
}

.die-face img {
  width: 28px;
  height: 28px;
  z-index: 1;
  position: relative;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
  transition: all 0.2s ease;
}

/* Selectable state */
.die.selectable {
  cursor: pointer;
}

.die.selectable:hover .die-inner {
  transform: rotateY(15deg) rotateX(5deg) scale(1.05);
}

.die.selectable:hover .die-face {
  background: linear-gradient(145deg, #f8f9fa, #e9ecef);
  box-shadow: 
    0 6px 12px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.die.selectable:hover .die-face img {
  transform: scale(1.1);
}

/* Selected state */
.die.selected .die-face {
  background: linear-gradient(145deg, #e3f2fd, #bbdefb);
  border-color: #2196f3;
  box-shadow: 
    0 0 0 3px rgba(33, 150, 243, 0.3),
    0 6px 16px rgba(33, 150, 243, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  animation: selected-pulse 2s infinite;
}

.die.selected .die-inner {
  transform: scale(1.1);
}

@keyframes selected-pulse {
  0%, 100% {
    box-shadow: 
      0 0 0 3px rgba(33, 150, 243, 0.3),
      0 6px 16px rgba(33, 150, 243, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);
  }
  50% {
    box-shadow: 
      0 0 0 6px rgba(33, 150, 243, 0.4),
      0 8px 20px rgba(33, 150, 243, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);
  }
}

/* Mana dice */
.die.mana .die-face {
  background: linear-gradient(145deg, #e8f5e8, #c8e6c8);
  border-color: #4caf50;
  position: relative;
}

.die.mana .die-face::before {
  background: linear-gradient(135deg, 
    rgba(76, 175, 80, 0.2) 0%, 
    rgba(76, 175, 80, 0.1) 50%, 
    rgba(0, 0, 0, 0.05) 100%);
}

/* Selection indicator */
.selection-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #4caf50, #45a049);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
  animation: check-bounce 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.check-mark {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

@keyframes check-bounce {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

/* Mana indicator */
.mana-indicator {
  position: absolute;
  bottom: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #ff9800, #f57c00);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9;
}


/* Kość z maną */
.die.mana {
  border: 2px dashed #28a745;
  background-color: #e6ffec;
}

/* Opcjonalna ikonka many */
.die.mana::after {
  content: '🪄';
  position: absolute;
  bottom: -6px;
  right: -6px;
  font-size: 14px;
  background: white;
  border-radius: 50%;
  padding: 2px;
  box-shadow: 0 0 3px rgba(0, 0, 0, 0.2);
}
</style>
