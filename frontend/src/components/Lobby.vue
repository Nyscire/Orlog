<template>
  <div class="lobby">
    <PlayerNameInput />
  </div>
</template>

<script>
import PlayerMenu from '../components/PlayerMenu.vue';
import socket from '../socket';

export default {
  name: 'Lobby',
  components: {
    PlayerMenu
  },
  mounted() {
    socket.on('game_data', (data) => {
      // Przechodzimy do GameBoard.vue z przekazaniem danych gry
      this.$router.push({ name: 'Game', state: { gameData: data } });
    });
  }
};
</script>

<style scoped>
.lobby {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
</style>
