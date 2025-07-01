<template>
  <GameBoard />
</template>

<script setup>
import GameBoard from './components/GameBoard.vue'
</script>

<style>
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #f8f9fa;
}

#app {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>