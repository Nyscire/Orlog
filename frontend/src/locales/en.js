// English texts. Same keys as pl.js.

const FACES = {
  axe: ['axe', 'axes'],
  arrow: ['arrow', 'arrows'],
  helmet: ['helmet', 'helmets'],
  shield: ['shield', 'shields']
}
const BONUS_PART = { axe: 'attack', arrow: 'attack', helmet: 'defence', shield: 'defence' }

const count = (n, [one, many]) => `${n} ${n === 1 ? one : many}`

function faceCounts(dice) {
  const counts = { axe: 0, arrow: 0, helmet: 0, shield: 0 }
  let mana = 0
  for (const die of dice || []) {
    if (die.stat in counts) counts[die.stat] += 1
    if (die.stat === 'mana') mana += 1
    if (die.gives_mana) mana += 1
  }
  return { counts, mana }
}

export const en = {
  menu: {
    subtitle: 'A dice game for two warriors',
    yourName: 'Your name',
    namePlaceholder: 'e.g. Eivor',
    godsLabel: 'Gods you take into the game',
    godsHint: 'You can buy their favors with mana during the game.',
    loadingGods: 'Loading gods from the server…',
    costs: 'Mana: {costs}',
    join: 'Join the game',
    playWith: 'Play with: {names}',
    gameInProgress: 'A game is in progress: {players}. If that is you, enter the same name to rejoin.',
    and: ' and ',
    waitingTitle: 'Waiting for the second player',
    playingAs: 'Playing as',
    withGods: 'gods: {gods}.',
    waitingHint: 'The other player opens the same page and enters their name.',
    changeChoice: 'Change name or gods',
    howToPlay: 'How to play?',
    settings: 'Settings',
    status: {
      offline: 'No connection to the server. Check that the backend is running (python main.py).',
      joined: 'Connected to the server',
      inProgress: 'Connected · a game is in progress on the server',
      waiting: 'Connected · waiting for an opponent: {names}',
      empty: 'Connected · nobody is waiting yet'
    }
  },

  board: {
    selfOffline: 'Lost connection to the server. Reconnecting…',
    opponentOffline: 'is offline. The game will wait until they come back with the same name. You can also end the game.',
    endGame: 'End the game'
  },

  stage: {
    waiting: 'Waiting for players',
    dice: 'Dice phase',
    gods: 'God favors',
    battle: 'Battle!',
    finished: 'Game over',
    unknown: 'Unknown phase'
  },

  neutral: {
    round: 'Round {n}',
    yourTurn: 'Your turn',
    turnOf: 'Turn:',
    howToPlay: 'How to play?',
    settings: 'Settings',
    leave: 'Leave game',
    leaveConfirm: 'End the game for both players?',
    leaveYes: 'Yes, leave',
    no: 'No',
    yourSaved: 'Your kept dice',
    opponentSaved: "Opponent's kept dice",
    nothingSaved: 'Nothing kept yet',
    youWin: 'You win!',
    winnerIs: '{name} wins',
    newGame: 'New game',
    hint: {
      waiting: 'Waiting for the second player…',
      opponentRolling: '{name} is rolling…',
      lastThrow: 'Last roll: all rolled dice will be kept.',
      pickDice: 'Click the dice you want to keep and confirm. You will reroll the rest.',
      opponentChoosing: '{name} is choosing a god favor…',
      pickGod: 'Pick a favor level and click "Choose", or skip the favor. Available mana: {mana}.'
    }
  },

  player: {
    yourTurn: 'Your turn',
    rollsLeft: 'Rolls left: {n}',
    rollsTitle: 'How many times you can still roll this round',
    pickDice: 'Choose dice',
    yourDice: 'Your dice',
    selected: 'Selected: {n}',
    confirmLast: 'Keep all (last roll)',
    confirmSelected: 'Keep selected ({n})',
    rerollAll: 'Reroll all',
    pickGod: 'Choose a god',
    yourGods: 'Your gods',
    chosen: 'Chosen: {god}',
    skipGod: 'Skip the favor this round'
  },

  stats: {
    hp: 'HP',
    hpTitle: 'Health: {hp} of {max}. Whoever drops to zero loses.',
    mana: 'Mana',
    manaTitle: 'Mana: used to buy god favors. Mana from kept dice is added after the dice phase.',
    fromDice: '+{n} from dice'
  },

  opponent: {
    roll: "Opponent's roll"
  },

  dice: {
    axe: { name: 'Axe', desc: 'Melee attack: 1 damage. Blocked by an opponent\'s helmet.' },
    arrow: { name: 'Arrow', desc: 'Ranged attack: 1 damage. Blocked by an opponent\'s shield.' },
    helmet: { name: 'Helmet', desc: 'Defence: blocks 1 opponent axe.' },
    shield: { name: 'Shield', desc: 'Defence: blocks 1 opponent arrow.' },
    mana: { name: 'Mana', desc: 'Gives 1 mana. Mana is spent on god favors.' },
    manaBorder: 'Gold border: this die gives 1 extra mana.',
    manaBorderName: 'Gold border',
    manaBorderLegend: 'The die gives 1 extra mana, whatever its symbol.',
    extraMana: 'gives 1 extra mana',
    summary: dice => {
      const { counts, mana } = faceCounts(dice)
      const attack = ['axe', 'arrow'].filter(f => counts[f]).map(f => count(counts[f], FACES[f]))
      const defence = ['helmet', 'shield'].filter(f => counts[f]).map(f => count(counts[f], FACES[f]))
      const parts = []
      if (attack.length) parts.push(`Attack: ${attack.join(', ')}`)
      if (defence.length) parts.push(`Defence: ${defence.join(', ')}`)
      if (mana) parts.push(`Mana: +${mana}`)
      return parts.join(' · ')
    }
  },

  gods: {
    choose: 'Choose',
    level: 'Level {level}',
    levelText: 'Level {level}: {text}',
    costs: god => `Mana cost: ${god.mana_costs.join(' / ')}`,
    describe: god => {
      const v = (god.values || []).join(' / ')
      if (god.effect === 'damage') return `Deals ${v} damage to the opponent.`
      if (god.effect === 'heal') return `Restores ${v} HP to you.`
      if (god.effect === 'bonus') return `Adds ${v} ${FACES[god.stat]?.[1] || god.stat} to your ${BONUS_PART[god.stat] || 'dice'} this round.`
      return ''
    },
    levelEffect: ({ god, level }) => {
      const value = god.values?.[level - 1]
      const cost = god.mana_costs?.[level - 1]
      if (god.effect === 'damage') return `${value} damage (${cost} mana)`
      if (god.effect === 'heal') return `+${value} HP (${cost} mana)`
      if (god.effect === 'bonus') return `+${count(value, FACES[god.stat] || [god.stat, god.stat])} (${cost} mana)`
      return `${cost} mana`
    }
  },

  log: {
    title: 'Game log',
    empty: "Players' moves and battle results will appear here.",
    round: 'Round {n}',
    events: {
      round_start: p => `${p.leader} starts`,
      dice_summary: p => {
        const parts = ['axe', 'arrow', 'helmet', 'shield'].filter(f => p.counts?.[f]).map(f => count(p.counts[f], FACES[f]))
        let text = `${p.player}: ${parts.length ? parts.join(', ') : 'no weapons or defence'}.`
        if (p.mana) text += ` Mana from dice: ${p.mana}.`
        return text
      },
      mana_collected: p => `Mana from dice goes to the pool: ${p.gains.map(g => `${g.player} +${g.gained} (total ${g.total})`).join(', ')}.`,
      god_chosen: p => `${p.player} chooses the favor of ${p.god}, level ${p.level} (cost ${p.cost} mana).`,
      god_skipped: p => `${p.player} skips the god favor this round.`,
      god_effect: p => {
        const head = `${p.player} uses the favor of ${p.god}:`
        if (p.effect === 'damage') return `${head} ${p.target} loses ${p.value} HP and now has ${p.hp}.`
        if (p.effect === 'heal') return `${head} regains ${p.value} HP and now has ${p.hp}.`
        if (p.effect === 'bonus') return `${head} +${count(p.value, FACES[p.stat] || [p.stat, p.stat])} this round.`
        return `${head} ${p.effect}.`
      },
      god_failed: p => `${p.player} cannot use the favor of ${p.god}: not enough mana (${p.mana} of ${p.cost}).`,
      attack: p => {
        const parts = []
        if (p.arrow) parts.push(`${count(p.arrow, FACES.arrow)} against ${count(p.shield, FACES.shield)}`)
        if (p.axe) parts.push(`${count(p.axe, FACES.axe)} against ${count(p.helmet, FACES.helmet)}`)
        if (!parts.length) return `${p.attacker} does not attack: no arrows or axes.`
        const outcome = p.dmg
          ? `Deals ${p.dmg} damage, ${p.defender} now has ${p.hp} HP.`
          : `The defence blocks everything, ${p.defender} still has ${p.hp} HP.`
        return `${p.attacker} attacks: ${parts.join(', ')}. ${outcome}`
      },
      win: p => `Game over. ${p.winner} wins.`
    }
  },

  help: {
    title: 'How to play Orlog',
    lead: 'The first player to bring the opponent\'s health down to zero wins. Everyone starts with 21 HP.',
    roundTitle: 'How a round works',
    steps: [
      { title: 'Rolling dice.', text: 'Players take turns rolling six dice. After each roll you mark the dice you want to keep and reroll the rest. You get 3 rolls, and on the last one all dice are kept.' },
      { title: 'God favors.', text: 'Each player can buy a favor from one of their gods or skip it. A favor costs mana, and a higher level gives a stronger effect.' },
      { title: 'Battle.', text: 'Favors take effect, then the player who started the round attacks, followed by the other player. The other player starts the next round.' }
    ],
    diceTitle: 'Dice',
    attackTitle: 'How attacks are counted',
    attackText: 'Each arrow deals 1 damage unless a shield blocks it. Each axe deals 1 damage unless a helmet blocks it. For example, 3 arrows against 1 shield deal 2 damage.',
    manaTitle: 'Mana and gods',
    manaText: 'Mana from kept dice goes to the pool after the dice phase, and unspent mana carries over to later rounds. Before the game you choose up to 3 gods. Hover over a god card to see what it does; after picking a level you see its effect and cost.',
    ok: 'Got it',
    close: 'Close'
  },

  settings: {
    title: 'Settings',
    language: 'Language',
    theme: 'Colors',
    font: 'Font',
    size: 'Text size',
    done: 'Done',
    sample: 'Axe, arrow and shield',
    themes: {
      classic: 'Wood and gold',
      frost: 'Frozen north',
      ember: 'Ash and blood',
      forest: 'Forest moss'
    },
    fonts: {
      classic: 'Classic',
      medieval: 'Medieval',
      readable: 'Easy to read'
    },
    sizes: {
      normal: 'Normal',
      large: 'Large'
    }
  },

  errors: {
    game_finished: 'The game is already over.',
    wrong_stage: 'That is not possible in this phase.',
    not_your_turn: 'It is not your turn.',
    no_opponent: 'There is no opponent.',
    invalid_gods: 'Invalid choice of gods.',
    duplicate_gods: 'Each god can be chosen only once.',
    gods_count: 'Choose between 1 and {max} gods.',
    unknown_god: 'There is no god called {god}.',
    name_required: 'Enter a player name.',
    name_too_long: 'The name can have at most {max} characters.',
    name_taken: 'That name is already taken.',
    game_full: 'The game is already full.',
    cannot_start: 'The game cannot start yet.',
    game_in_progress: 'The game is still in progress.',
    invalid_dice: 'Invalid dice selection.',
    invalid_level: 'The favor level must be 1, 2 or 3.',
    not_enough_mana: 'Not enough mana: {god} at level {level} costs {cost} and you have {mana}.',
    join_first: 'Join the game first.',
    already_playing_as: 'You are already playing as {name}.',
    player_left: '{name} ended the game. You can start a new one.',
    unknown: 'Something went wrong ({code}).'
  }
}
