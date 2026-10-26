// English texts. Same keys as pl.js.

const FACES = {
  axe: ['axe', 'axes'],
  arrow: ['arrow', 'arrows'],
  helmet: ['helmet', 'helmets'],
  shield: ['shield', 'shields'],
  hand: ['hand', 'hands']
}
const DICE = ['die', 'dice']

const count = (n, [one, many]) => `${n} ${n === 1 ? one : many}`
const MANA = n => `${n} mana`
const SLASH = '\u00a0/\u00a0'
const HP = n => `${n} HP`
const faceList = faces => faces.map(f => FACES[f]?.[0] || f).join(', ')

// Favors: name, description (values of all levels), effect of one level and the log line
const FAVORS = {
  thor_strike: {
    name: "Thor's Strike",
    desc: v => `After battle, deals ${v} damage to the opponent.`,
    level: x => `${x} damage`,
    log: p => `${p.target} loses ${HP(p.value)}, ${p.hp} left.`
  },
  idun_rejuvenation: {
    name: "Idun's Rejuvenation",
    desc: v => `After battle, heals you for ${v} HP.`,
    level: x => `+${HP(x)}`,
    log: p => `+${HP(p.healed)}, now at ${p.hp}.`
  },
  vidar_might: {
    name: "Vidar's Might",
    desc: v => `Before battle, removes ${v} of the opponent's helmets.`,
    level: x => `−${count(x, FACES.helmet)} for the opponent`,
    log: p => (p.removed ? `${p.target} loses ${count(p.removed, FACES.helmet)}.` : `${p.target} has no helmets to remove.`)
  },
  ullr_aim: {
    name: "Ullr's Aim",
    desc: v => `Your arrows ignore ${v} of the opponent's shields.`,
    level: x => `arrows ignore ${count(x, FACES.shield)}`,
    log: p => `arrows ignore ${count(p.value, FACES.shield)}.`
  },
  heimdall_watch: {
    name: "Heimdall's Watch",
    desc: v => `After battle, +${v} HP per blocked attack.`,
    level: x => `+${HP(x)} per block`,
    log: p => `blocked attacks: ${p.blocked}, +${HP(p.healed)}, now at ${p.hp}.`
  },
  baldr_invulnerability: {
    name: "Baldr's Invulnerability",
    desc: v => `Each helmet and shield die counts ${v} extra.`,
    level: x => `+${x} per helmet and shield`,
    log: p => `defence +${count(p.helmets, FACES.helmet)}, +${count(p.shields, FACES.shield)}.`
  },
  brunhild_fury: {
    name: "Brunhild's Fury",
    desc: v => `Multiplies your axes ×${v} (rounded up).`,
    level: x => `axes ×${x}`,
    log: p => `axes: ${p.before} → ${p.after}.`
  },
  freyr_gift: {
    name: "Freyr's Gift",
    desc: v => `+${v} to the face you have the most of (axe, arrow, helmet, shield).`,
    level: x => `+${x} to your most common face`,
    log: p => (p.stat ? `+${count(p.value, FACES[p.stat])}.` : 'no axes, arrows, helmets or shields, so nothing happens.')
  },
  hel_grip: {
    name: "Hel's Grip",
    desc: v => `After battle, +${v} HP per damage from your axes.`,
    level: x => `+${HP(x)} per axe damage`,
    log: p => `axe damage: ${p.damage}, +${HP(p.healed)}, now at ${p.hp}.`
  },
  skadi_hunt: {
    name: "Skadi's Hunt",
    desc: v => `Each arrow die counts ${v} extra.`,
    level: x => `+${x} per arrow`,
    log: p => `+${count(p.added, FACES.arrow)}.`
  },
  skuld_claim: {
    name: "Skuld's Claim",
    desc: v => `After battle, the opponent loses ${v} mana per arrow you have.`,
    level: x => `−${MANA(x)} for the opponent per arrow`,
    log: p => `${p.target} loses ${MANA(p.destroyed)}, ${p.left} left.`
  },
  frigg_sight: {
    name: "Frigg's Sight",
    desc: v => `Before battle, rerolls ${v} chosen dice, yours or the opponent's.`,
    level: x => `reroll up to ${count(x, DICE)}`,
    log: p => `rerolled dice: own ${p.own}, opponent's ${p.opponent}.`
  },
  loki_trick: {
    name: "Loki's Trick",
    desc: v => `Bans ${v} chosen opponent dice for this round.`,
    level: x => `bans ${count(x, DICE)} of the opponent`,
    log: p => (p.banned.length ? `${p.target} loses for this round: ${faceList(p.banned)}.` : 'nothing to ban.')
  },
  freyja_plenty: {
    name: "Freyja's Plenty",
    desc: v => `Before battle, you roll ${v} extra dice.`,
    level: x => `+${count(x, DICE)}`,
    log: p => {
      let text = `extra dice: ${faceList(p.faces)}.`
      if (p.mana) text += ` Gold borders: +${p.mana} mana.`
      if (p.stolen) text += ` Hands steal ${MANA(p.stolen)}.`
      return text
    }
  },
  mimir_wisdom: {
    name: "Mimir's Wisdom",
    desc: v => `After battle, +${v} mana per damage taken.`,
    level: x => `+${MANA(x)} per damage taken`,
    log: p => `damage taken: ${p.damage}, +${MANA(p.gained)} (total ${p.total}).`
  },
  bragi_verve: {
    name: "Bragi's Verve",
    desc: v => `+${v} mana per hand die.`,
    level: x => `+${MANA(x)} per hand`,
    log: p => `hands: ${p.hands}, +${MANA(p.gained)} (total ${p.total}).`
  },
  odin_sacrifice: {
    name: "Odin's Sacrifice",
    desc: v => `After battle, sacrifice any HP and gain ${v} mana for each.`,
    level: x => `${MANA(x)} per 1 HP`,
    log: p => `sacrifices ${HP(p.sacrificed)} and gains ${MANA(p.gained)} (HP: ${p.hp}, mana: ${p.total}).`
  },
  var_bond: {
    name: "Var's Bond",
    desc: v => `After battle, +${v} HP per mana the opponent spent.`,
    level: x => `+${HP(x)} per opponent mana`,
    log: p => `the opponent spent ${MANA(p.spent)}, +${HP(p.healed)}, now at ${p.hp}.`
  },
  thrymr_theft: {
    name: "Thrymr's Theft",
    desc: v => `Lowers the opponent's favor by ${v} levels. Mana spent on it is lost.`,
    level: x => `opponent's favor −${count(x, ['level', 'levels'])}`,
    log: p => {
      if (!p.target_god) return `${p.target} chose no favor, nothing to lower.`
      if (!p.new_level) return `${p.target}: ${favorByGod(p.target_god)} is cancelled.`
      return `${p.target}: ${favorByGod(p.target_god)} drops from level ${p.old_level} to ${p.new_level}.`
    }
  },
  tyr_pledge: {
    name: "Tyr's Pledge",
    desc: v => `After battle, sacrifice any HP; the opponent loses ${v} mana for each.`,
    level: x => `−${MANA(x)} for the opponent per 1 HP`,
    log: p => `sacrifices ${HP(p.sacrificed)}, ${p.target} loses ${MANA(p.destroyed)} (${p.left} left).`
  }
}
const favor = effect => FAVORS[effect] || { name: effect, desc: () => '', level: () => '', log: () => '' }
const favorByGod = name => {
  const key = Object.keys(FAVORS).find(k => k.startsWith(name.toLowerCase() + '_'))
  return key ? FAVORS[key].name : name
}

function faceCounts(dice) {
  const counts = { axe: 0, arrow: 0, helmet: 0, shield: 0, hand: 0 }
  let mana = 0
  for (const die of dice || []) {
    if (die.stat in counts) counts[die.stat] += 1
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
    manaTitle: 'Mana: used to buy god favors. After the dice phase gold borders give mana and hands steal it from the opponent.',
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
    hand: { name: 'Hand', desc: 'Steals 1 mana from the opponent, if they have any.' },
    manaBorder: 'Gold border: this die gives 1 mana.',
    manaBorderName: 'Gold border',
    manaBorderLegend: 'The die gives 1 mana, whatever its symbol.',
    extraMana: 'gives 1 mana',
    // "2 axes, 1 arrow · 1 helmet · 2 hands · +3 mana"
    summary: dice => {
      const { counts, mana } = faceCounts(dice)
      const group = faces => faces.filter(f => counts[f]).map(f => count(counts[f], FACES[f])).join(', ')
      const parts = [group(['axe', 'arrow']), group(['helmet', 'shield']), group(['hand'])].filter(Boolean)
      if (mana) parts.push(`+${MANA(mana)}`)
      return parts.join(' · ')
    }
  },

  gods: {
    choose: 'Choose',
    level: 'Level {level}',
    levelText: 'Level {level}: {text}',
    name: god => god.name,
    favor: god => favor(god.effect).name,
    costs: god => `Mana cost: ${god.mana_costs.join(SLASH)}`,
    describe: god => favor(god.effect).desc((god.values || []).join(SLASH)),
    levelEffect: ({ god, level }) => {
      const value = god.values?.[level - 1]
      const cost = god.mana_costs?.[level - 1]
      return `${favor(god.effect).level(value)} (${MANA(cost)})`
    },
    phase: {
      first: 'Start of battle',
      before: 'Before battle',
      after: 'After battle'
    },
    sacrifice: 'Sacrifice',
    sacrificed: 'Sacrifices {n} HP',
    less: 'Less',
    more: 'More',
    sacrificeResult: ({ god, level, amount }) => {
      const value = god.values?.[level - 1] || 0
      return god.effect === 'tyr_pledge'
        ? `opponent −${MANA(value * amount)}`
        : `+${MANA(value * amount)}`
    },
    pickTargets: ({ picked, max }) => `Pick dice on the table: ${picked} of ${max}`,
    pickTargetsHint: ({ god, max, any }) => any
      ? `${favor(god.effect).name}: click up to ${count(max, DICE)} on the table (yours or the opponent's) to reroll.`
      : `${favor(god.effect).name}: click up to ${count(max, DICE)} of the opponent's on the table to ban.`
  },

  log: {
    title: 'Game log',
    empty: "Players' moves and battle results will appear here.",
    round: 'Round {n}',
    events: {
      round_start: p => `${p.leader} starts`,
      dice_summary: p => {
        const parts = ['axe', 'arrow', 'helmet', 'shield', 'hand'].filter(f => p.counts?.[f]).map(f => count(p.counts[f], FACES[f]))
        let text = `${p.player}: ${parts.length ? parts.join(', ') : 'no weapons or defence'}.`
        if (p.mana) text += ` Gold borders: ${p.mana}.`
        return text
      },
      mana_collected: p => `Mana from gold borders goes to the pool: ${p.gains.map(g => `${g.player} +${g.gained} (total ${g.total})`).join(', ')}.`,
      mana_stolen: p => (p.amount
        ? `${p.thief} steals ${MANA(p.amount)} (${count(p.hands, FACES.hand)}). Mana: ${p.thief} ${p.thief_total}, ${p.victim} ${p.victim_total}.`
        : `${p.thief}: ${count(p.hands, FACES.hand)} but nothing to steal, ${p.victim} has no mana.`),
      god_chosen: p => {
        let text = `${p.player} chooses ${favorByGod(p.god)}, level ${p.level} (cost ${MANA(p.cost)}).`
        if (p.amount) text += ` Will sacrifice ${HP(p.amount)}.`
        if (p.targets) {
          const n = (p.targets.own || []).length + (p.targets.opponent || []).length
          text += ` Dice picked: ${n}.`
        }
        return text
      },
      god_skipped: p => `${p.player} skips the god favor this round.`,
      god_effect: p => `${p.player} · ${favor(p.effect).name}: ${favor(p.effect).log(p)}`,
      god_failed: p => `${p.player} · ${favorByGod(p.god)}: not enough mana (${p.mana} of ${p.cost}), the favor fails.`,
      god_cancelled: p => `${p.player} · ${favorByGod(p.god)}: lost to Thrymr's Theft, the ${MANA(p.cost)} spent is not returned.`,
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
      { title: 'Mana.', text: 'Each gold border gives 1 mana, and each hand steals 1 mana from the opponent if they have any.' },
      { title: 'God favors.', text: 'Each player can buy a favor from one of their gods or skip it. A higher level costs more and gives a stronger effect.' },
      { title: 'Battle.', text: 'First the "before battle" favors take effect, then the player who started the round attacks, followed by the other player, and finally the "after battle" favors. The other player starts the next round.' }
    ],
    diceTitle: 'Dice',
    attackTitle: 'How attacks are counted',
    attackText: 'Each arrow deals 1 damage unless a shield blocks it. Each axe deals 1 damage unless a helmet blocks it. For example, 3 arrows against 1 shield deal 2 damage.',
    manaTitle: 'Mana and gods',
    manaText: 'Mana from dice goes to the pool after the dice phase, and unspent mana carries over to later rounds. Before the game you choose up to 3 of 20 gods. Hover over a god card to see what it does; after picking a level you see its effect and cost. A few favors need an extra choice: Frigg and Loki pick dice on the table, Odin and Tyr choose how much HP to sacrifice.',
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
    invalid_amount: 'You can sacrifice between 1 and {max} HP.',
    not_enough_hp: 'You do not have enough HP to sacrifice.',
    invalid_targets: 'Invalid dice choice for the favor.',
    targets_count: 'Pick between 1 and {max} dice.',
    join_first: 'Join the game first.',
    already_playing_as: 'You are already playing as {name}.',
    player_left: '{name} ended the game. You can start a new one.',
    unknown: 'Something went wrong ({code}).'
  }
}
