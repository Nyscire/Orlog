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
  transition: border-color 0.2s, background-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
}
.die.selected {
  border-color: blue;
}
.die.mana {
  background-color: #e0ffe0;
}
img {
  max-width: 100%;
  max-height: 100%;
}
</style>
