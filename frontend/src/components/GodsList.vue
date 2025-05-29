<template>
  <div class="gods-list">
    <GodsDisplay
      v-for="god in gods"
      :key="god.name"
      :gods="[god]"
      :chosenGod="chosenGod"
      :readonly="readonly"
      @choose-god="$emit('choose-god', god.name)"
    />
  </div>
</template>

<script>
import GodsDisplay from './GodsDisplay.vue'

export default {
  components: { GodsDisplay },
  props: {
    gods: Array,
    chosenGod: Object,
    readonly: Boolean
  }
}
</script>

<style scoped>
.gods-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}
</style>
