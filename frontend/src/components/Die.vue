<template>
  <div
    class="die"
    :class="{
      selected: selected,
      mana: die.gives_mana
    }"
  >
    <img :src="`/img/icons/${die.stat}.svg`" :alt="die.stat" />
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
  }
}
</script>

<style scoped>
.die {
  width: 48px;
  height: 48px;
  padding: 4px;
  border: 2px solid transparent;
  border-radius: 8px;
  background-color: #f0f0f0;
  box-sizing: border-box;
  transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

/* Zaznaczona kość */
.die.selected {
  outline: 3px solid #959595;
  filter: brightness(1.1);
}
.selection-mark {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 1rem;
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
