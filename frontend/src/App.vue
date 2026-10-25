<template>
  <GameBoard />
</template>

<script setup>
import GameBoard from './components/GameBoard.vue'
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  min-height: 100%;
  background-color: #f8f9fa;
}

#app {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>