<template>
  <div class="name-entry">
    <h2>Wprowadź swoją nazwę gracza</h2>
    <input v-model="name" placeholder="Twoja nazwa" />
    <button @click="submit" :disabled="!name">Zatwierdź</button>
    <p v-if="submitted">Oczekiwanie na drugiego gracza...</p>
  </div>
</template>

<script>
export default {
  name: 'PlayerMenu',
  data() {
    return {
      name: '',
      submitted: false
    };
  },
  methods: {
    submit() {
      this.submitted = true;
      this.$emit('name-submitted', this.name);
    }
  }
};
</script>

<style scoped>
.name-entry {
  text-align: center;
  margin-top: 2rem;
}
</style>
