import { defineStore } from 'pinia'

export const useGameStore = defineStore('game', {
  state: () => ({
    dice: [],
    selectedGod: null,
    players: []
  })
})
