<template>
  <div class="game-container">
    <PlayerMenu v-if="!playerName" @name-submitted="submitName" />

    <div v-else class="game-interface">
      <!-- Opponent -->
      <div class="player-section opponent compact-layout board-section-padding">
        <div class="horizontal-group">
          <div class="actions-and-stats">
            <PlayerStats :name="opponent.name" :hp="opponent.HP" :mana="opponent.Mana" />
          </div>
          <div class="dice-section">
            <DiceDisplay
              :dice="opponent.rolled_dice"
              title="Kości przeciwnika"
              :selectable="false"
              @toggle-selection="toggleDieSelection"
            />
          </div>
          <div class="gods-section">
            <GodsOpponentDisplay
              :gods="opponent.gods"
              :readonly="true" 
            />
          </div>
        </div>
      </div>

      <!-- Neutral Zone -->
      <div class="neutral-section board-section-padding">
        <div class="stage-indicator">
          <transition name="stage-fade" mode="out-in">
            <div v-if="data.stage === 'dice'" class="stage-badge dice-stage">
              <span class="stage-icon">🎲</span>
              <span>Etap: Wybór kości</span>
            </div>
            <div v-else class="stage-badge gods-stage">
              <span class="stage-icon">⚡</span>
              <span>Etap: Wybór boga</span>
            </div>
          </transition>
          
          <div class="turn-indicator">
            <span class="turn-label">Aktualny gracz:</span>
            <span class="turn-player" :class="{ 'my-turn': isMyTurn }">{{ data.active_player }}</span>
          </div>
        </div>

        <div class="neutral-content">
          <div class="neutral-grid">
            <div class="neutral-block">
              <h4>Zapisane kości przeciwnika</h4>
              <div class="saved-dice-container">
                <DiceDisplay :dice="opponent.saved_dice" title="" />
              </div>
            </div>

            <div class="neutral-block god-display-block">
              <h4>Wybrany bóg przeciwnika</h4>
              <transition name="god-appear">
                <GodsNeutralDisplay
                  v-if="opponent.chosen_god && opponent.chosen_god.name"
                  :god="opponent.chosen_god"
                />
              </transition>
            </div>

            <div class="neutral-block god-display-block">
              <h4>Twój wybrany bóg</h4>
              <transition name="god-appear">
                <GodsNeutralDisplay
                  v-if="player.chosen_god && player.chosen_god.name"
                  :god="player.chosen_god"
                />
              </transition>
            </div>

            <div class="neutral-block">
              <h4>Twoje zapisane kości</h4>
              <div class="saved-dice-container">
                <DiceDisplay :dice="player.saved_dice" title="" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Player -->
      <div class="player-section self compact-layout board-section-padding">
        <div class="horizontal-group">
          <div class="actions-and-stats">
            <PlayerStats :name="player.name" :hp="player.HP" :mana="player.Mana" />
            <div class="rolls-counter">
              <span class="rolls-label">Pozostałe rzuty:</span>
              <span class="rolls-count">{{ player.rzuty }}</span>
            </div>
          </div>
          
          <div class="dice-section">
            <transition name="dice-roll" mode="out-in">
              <DiceDisplay
                :key="diceKey"
                :dice="player.rolled_dice"
                title="Wylosowane Kości"
                :selectable="canSelectDice"
                :selected-indexes="selectedDiceIndexes"
                @toggle-selection="toggleDieSelection"
              />
            </transition>
            
            <transition name="slide-up">
              <div v-if="canSelectDice" class="confirm-dice-wrapper">
                <button class="confirm-dice-button" @click="confirmDice">
                  <span class="button-icon">✓</span>
                  Zatwierdź kości
                </button>
              </div>
            </transition>
          </div>

          <div class="gods-section">
            <GodsPlayerDisplay
              :gods="player.gods"
              :readonly="!canSelectGod"
              @choose-god="chooseGod"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import socket from '../socket';
import PlayerStats from './PlayerStats.vue'
import DiceDisplay from './DiceDisplay.vue'
import GodsPlayerDisplay from './GodsPlayerDisplay.vue'
import GodsNeutralDisplay from './GodsNeutralDisplay.vue'
import GodsOpponentDisplay from './GodsOpponentDisplay.vue'
import PlayerMenu from './PlayerMenu.vue';

export default {
  components: {
    PlayerStats,
    DiceDisplay,
    GodsPlayerDisplay,
    GodsOpponentDisplay,
    GodsNeutralDisplay,
    PlayerMenu
  },
  data() {
    return {
      tempName: '',
      playerName: '',
      data: {},
      selectedDiceIndexes: [],
      diceKey: 0
    }
  },
  computed: {
    player() {
      return this.data.players?.find(p => p.name === this.playerName) || {}
    },
    opponent() {
      return this.data.players?.find(p => p.name !== this.playerName) || {}
    },
    isMyTurn() {
      return this.data.active_player === this.playerName
    },
    stage() {
      return this.data.stage
    },
    canSelectDice() {
      return this.isMyTurn && this.stage === 'dice';
    },
    canSelectGod() {
      return this.isMyTurn && this.stage === 'gods';
    }
  },
  mounted() {
    socket.on('connect', () => {
      console.log('Połączono z serwerem Socket.IO');
    });

    socket.on('game_state', (data) => {
      this.data = data;
      this.diceKey++; // Force dice re-render for animations
    });
  },
  methods: {
    submitName(name) {
      this.playerName = name;
      socket.emit('submit_player_name', name);
    },
    updateGameState(data) {
      // Aktualizacja stanu gry na podstawie otrzymanych danych
    },
    sendPlayerAction(action) {
      socket.emit('player_action', action);
    },

    toggleDieSelection(index) {
      const pos = this.selectedDiceIndexes.indexOf(index)
      if (pos >= 0) this.selectedDiceIndexes.splice(pos, 1)
      else this.selectedDiceIndexes.push(index)
    },
    
    confirmDice() {
      if (!this.canSelectDice) return;

      let selectedDice;

      if (this.player.rzuty === 1) {
        selectedDice = this.player.rolled_dice.slice();
        this.selectedDiceIndexes = this.player.rolled_dice.map((_, i) => i);
      } else {
        selectedDice = this.player.rolled_dice.filter((_, i) =>
          this.selectedDiceIndexes.includes(i)
        );
      }

      this.player.saved_dice.push(...selectedDice);
      this.player.rolled_dice = this.player.rolled_dice.filter((_, i) =>
        !this.selectedDiceIndexes.includes(i)
      );

      socket.emit('confirm_dice', {
        player: this.playerName,
        selectedIndexes: this.selectedDiceIndexes
      });

      this.selectedDiceIndexes = [];
    },

    chooseGod({ godName, level }) {
      if (!this.canSelectGod) return;

      const god = this.player.gods.find(g => g.name === godName);
      if (god) {
        this.player.chosen_god = {
          ...god,
          level
        };
      }
      socket.emit('choose_god', {
        player: this.playerName,
        godName,
        level
      });
    },

    chooseGodLevel({ godName, level }) {
      const god = this.player.gods.find(g => g.name === godName)
      if (god) {
        god.level = level
        if (this.player.chosen_god && this.player.chosen_god.name === godName) {
          this.player.chosen_god.level = level
        }
      }
    },
    
    toggleStage() {
      this.data.stage = this.data.stage === 'dice' ? 'gods' : 'dice'
    }
  }
}
</script>

<style scoped>
.game-container {
  padding: 1rem;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.game-interface {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.player-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.player-section:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.opponent {
  border-left: 4px solid #e74c3c;
}

.self {
  border-left: 4px solid #27ae60;
}

.horizontal-group {
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  gap: 2rem;
  align-items: start;
}

.actions-and-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dice-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  min-height: 120px;
}

.gods-section {
  min-width: 300px;
}

.neutral-section {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 2rem;
  min-height: 400px;
}

.stage-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
}

.stage-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  font-size: 1.1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.dice-stage {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.gods-stage {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
}

.stage-icon {
  font-size: 1.3rem;
}

.turn-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
}

.turn-label {
  color: #666;
}

.turn-player {
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 15px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.turn-player.my-turn {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  transform: scale(1.05);
}

.neutral-content {
  height: 100%;
}

.neutral-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  height: 100%;
}

.neutral-block {
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;
}

.neutral-block:hover {
  background: rgba(248, 249, 250, 1);
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.god-display-block {
  justify-content: center;
}

.saved-dice-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
}

.rolls-counter {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.rolls-label {
  display: block;
  font-size: 0.9rem;
  opacity: 0.9;
}

.rolls-count {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  margin-top: 0.25rem;
}

.confirm-dice-wrapper {
  margin-top: 1rem;
}

.confirm-dice-button {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
  transition: all 0.3s ease;
}

.confirm-dice-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
}

.button-icon {
  font-size: 1.2rem;
}

h3, h4 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 1rem;
}

h4 {
  font-size: 1rem;
  font-weight: 600;
  opacity: 0.8;
}

/* Animations */
.stage-fade-enter-active, .stage-fade-leave-active {
  transition: all 0.5s ease;
}
.stage-fade-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
.stage-fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.dice-roll-enter-active {
  transition: all 0.6s ease;
}
.dice-roll-enter-from {
  opacity: 0;
  transform: scale(0.8) rotateY(180deg);
}

.god-appear-enter-active, .god-appear-leave-active {
  transition: all 0.5s ease;
}
.god-appear-enter-from, .god-appear-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.slide-up-enter-active {
  transition: all 0.4s ease;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive Design */
@media (max-width: 1440px) {
  .horizontal-group {
    grid-template-columns: 220px 1fr 280px;
    gap: 1.5rem;
  }
  
  .neutral-grid {
    gap: 1rem;
  }
}

@media (max-width: 1200px) {
  .horizontal-group {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .neutral-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .gods-section {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .neutral-grid {
    grid-template-columns: 1fr;
  }
  
  .game-container {
    padding: 0.5rem;
  }
}
</style>