<template>
  <div class="name-entry">
    <h2>Wprowadź swoją nazwę gracza</h2>
    <input v-model="name" placeholder="Twoja nazwa" />
    <button @click="submit" :disabled="!name.trim()">Zatwierdź</button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="submitted">Oczekiwanie na drugiego gracza...</p>
  </div>
</template>

<script>
export default {
  name: 'PlayerMenu',
  props: {
    error: String
  },
  emits: ['name-submitted'],
  data() {
    return {
      name: '',
      submitted: false
    };
  },
  methods: {
    submit() {
      this.submitted = true;
      this.$emit('name-submitted', this.name.trim());
    }
  }
};
</script>

<style scoped>
.name-entry {
  text-align: center;
  margin-top: 2rem;
}
.error {
  color: #c62828;
  font-weight: 600;
}
</style>
