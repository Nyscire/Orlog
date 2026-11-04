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
      if (p.mana) text += ` Coins: +${p.mana} mana.`
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
    loadingGods: 'Loading gods from the server…',
    costs: 'Mana: {costs}',
    waitingTitle: 'Waiting for the second player',
    playingAs: 'Playing as',
    withGods: 'gods: {gods}.',
    waitingHint: 'The other player picks this table from the list in the menu and clicks "Take a seat".',
    howToPlay: 'How to play?',
    settings: 'Settings',
    newWindow: 'New window',
    status: {
      offline: 'No connection to the server. Check that the backend is running (python main.py).',
      offlineApp: 'No connection to the server {server}. You can change the address in the settings.',
      noServer: 'Enter the game server address in the settings.',
      joined: 'Connected to the server',
      online: 'Connected · {tables}'
    }
  },

  lobby: {
    title: 'Tables',
    count: ({ n }) => `${n} ${n === 1 ? 'table' : 'tables'}`,
    namePlaceholder: 'Table name (optional)',
    create: 'Open a table',
    join: 'Take a seat',
    busy: 'Playing',
    empty: 'There are no tables yet. Open the first one and the other player will pick it from the list.',
    defaultName: "{host}'s table",
    waitingFor: '{name} is waiting',
    playing: '{players} · round {round}',
    finished: '{players} · game over',
    needSetup: 'Enter your name and choose gods to take a seat.',
    full: 'The server already has the maximum of {max} tables. Take a seat at one from the list.',
    leave: 'Leave the table',
    mode: 'Game type',
    normal: 'Normal',
    ranked: 'Ranked',
    normalHint: "Doesn't affect the ranking. Guests can join too.",
    rankedHint: "The result changes both players' rating. Signed-in players only.",
    rankedLogin: 'Ranked games are for signed-in players.',
    loginToJoin: 'Signed-in only'
  },

  board: {
    selfOffline: 'Lost connection to the server. Reconnecting…',
    opponentOffline: 'is offline. The game will wait until they come back. You can also leave the table.',
    opponentOfflineRanked: "is offline. If they don't come back within {s} s, you win by forfeit.",
    endGame: 'Leave the table'
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
    leave: 'Leave table',
    leaveConfirm: 'Leave the table? The game will end.',
    leaveConfirmRanked: 'Leaving a ranked game counts as a loss by forfeit. Leave?',
    ratingChange: 'Rating: {before} → {after} ({delta})',
    leaveYes: 'Yes, leave',
    tableCode: 'Table code: {code}',
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
    manaTitle: 'Mana: used to buy god favors. After the dice phase dice with a coin give mana and hands steal it from the opponent.',
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
    coin: 'Coin in the corner: this die gives 1 mana.',
    coinName: 'Coin in the corner',
    coinLegend: 'A die with a coin gives 1 mana, whatever its symbol.',
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
        if (p.mana) text += ` Dice with a coin: ${p.mana}.`
        return text
      },
      mana_collected: p => `Mana from coins goes to the pool: ${p.gains.map(g => `${g.player} +${g.gained} (total ${g.total})`).join(', ')}.`,
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
      win: p => `Game over. ${p.winner} wins.`,
      forfeit: p => `${p.loser} left the game. ${p.winner} wins by forfeit.`
    }
  },

  help: {
    title: 'How to play Orlog',
    lead: 'The first player to bring the opponent\'s health down to zero wins. Everyone starts with 21 HP.',
    roundTitle: 'How a round works',
    steps: [
      { title: 'Rolling dice.', text: 'Players take turns rolling six dice. After each roll you mark the dice you want to keep and reroll the rest. You get 3 rolls, and on the last one all dice are kept.' },
      { title: 'Mana.', text: 'Each die with a coin in the corner gives 1 mana, and each hand steals 1 mana from the opponent if they have any.' },
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
    server: 'Game server',
    serverPlaceholder: 'e.g. 192.168.0.10 or https://orlog.example.com',
    serverConnect: 'Connect',
    serverCurrent: 'Current: {url}.',
    serverMissing: 'Enter the address of the server the game should connect to.',
    serverFormat: 'Without a port number the game connects to port 5000.',
    serverInvalid: 'This does not look like a server address.',
    serverReset: 'Restore default',
    newWindow: 'New player window',
    newWindowHint: 'Opens the game in another window as a separate player, e.g. to try a game on one computer. Shortcut: Ctrl+Shift+N.',
    version: 'Orlog {version}',
    sample: 'Axe, arrow and shield',
    themes: {
      classic: 'Wood and gold',
      frost: 'Frozen north',
      ember: 'Ash and blood',
      forest: 'Forest moss',
      night: 'Polar night',
      abyss: "Hel's abyss"
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

  account: {
    login: 'Sign in',
    register: 'Create account',
    loginTitle: 'Sign in',
    registerTitle: 'New account',
    registerLead: 'Your account keeps your results, match history and god stats, and lets you play ranked games.',
    loginOrEmail: 'Username or email',
    loginLabel: 'Username',
    loginHint: '3–20 characters: letters, digits, dot, dash, underscore. Other players see it.',
    email: 'Email',
    emailHint: 'Only for recovering your password. Nobody else sees it.',
    password: 'Password',
    passwordRepeat: 'Repeat password',
    passwordMismatch: "The passwords don't match.",
    newPassword: 'New password',
    loginButton: 'Sign in',
    registerButton: 'Create account',
    wait: 'One moment…',
    forgot: 'Forgot your password?',
    noAccount: 'No account yet? Create one',
    haveAccount: 'Already have an account? Sign in',
    resetTitle: 'New password',
    resetLead: "Enter your username or email. We'll email you a six-digit code for setting a new password.",
    sendCode: 'Send code',
    codeSent: 'If the account exists, the code is on its way to its email (check spam too). The code works for 15 minutes.',
    code: 'Code from the email',
    setPassword: 'Set password and sign in',
    resend: 'Send the code again',
    backToLogin: 'Back to sign in',
    signedInAs: 'Signed in as',
    profile: 'Profile',
    logout: 'Sign out',
    expired: 'Your session has expired. Sign in again to play on your account.'
  },

  profile: {
    myTab: 'My profile',
    playerTab: 'Player {name}',
    loading: 'Loading…',
    missing: 'There is no player {name}.',
    since: 'Playing since {date}',
    position: ({ n }) => `#${n} in the ranking`,
    noRanked: 'no ranked games yet',
    peak: 'best {n}',
    games: 'Games',
    wins: 'Wins',
    losses: 'Losses',
    winRate: 'Win rate',
    ranked: 'Ranked',
    normal: 'Normal',
    record: ({ games, wins, losses }) => `${games} (${wins}–${losses})`,
    godsTitle: 'Gods',
    gamesShort: ({ n }) => `${n} ${n === 1 ? 'game' : 'games'}`,
    godRecord: 'Won {wins} of {games}',
    historyTitle: 'Recent games',
    noGames: 'No games yet.',
    win: 'Win',
    loss: 'Loss',
    vs: 'vs',
    guest: 'guest',
    forfeit: 'forfeit',
    rounds: ({ n }) => `${n} ${n === 1 ? 'round' : 'rounds'}`,
    more: 'Show older'
  },

  ranking: {
    title: 'Ranking',
    lead: 'Only ranked games change the rating. Everyone starts at 1000, and beating a stronger opponent gives more.',
    empty: 'Nobody has played a ranked game yet.',
    player: 'Player',
    rating: 'Rating',
    record: 'W–L',
    games: 'Games'
  },

  update: {
    readyTitle: 'Version {version} is ready',
    readyText: 'It installs when you close the game, or now after a restart.',
    readyTextPassword: 'Installing asks for your password, then the game restarts.',
    availableTitle: 'Version {version} is available',
    availableText: 'Download the new file from the game releases page.',
    restart: 'Restart now',
    install: 'Install',
    download: 'Download',
    later: 'Later'
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
    already_seated: 'You already have a seat as {name}.',
    player_left: '{name} left the table. Wait for a new opponent or go back to the table list.',
    opponent_forfeit: '{name} left the ranked game, so you win by forfeit. Wait for a new opponent or go back to the table list.',
    login_invalid: 'The username must have {min}–{max} characters: letters, digits, dot, dash or underscore.',
    login_taken: 'This username is already taken.',
    email_invalid: "That doesn't look like an email address.",
    email_taken: 'There is already an account with this email. You can recover its password.',
    password_too_short: 'The password must have at least {min} characters.',
    password_too_long: 'The password can have at most {max} characters.',
    bad_credentials: 'Wrong username or password.',
    too_many_attempts: 'Too many failed attempts. Try again in {minutes} min.',
    reset_code_invalid: 'The code is wrong or has expired. Send a new one.',
    leave_table_first: 'Leave the table first.',
    ranked_login_required: 'Ranked games are for signed-in players only.',
    name_reserved: 'This name belongs to a registered player. If that is you, sign in.',
    account_busy: 'You are already playing on this account at another table or in another window.',
    table_not_found: 'This table is gone or its host is offline.',
    table_full: 'There is no free seat at this table.',
    too_many_tables: 'The server already has {max} tables. Take a seat at one from the list.',
    table_name_too_long: 'The table name can have at most {max} characters.',
    invalid_table_name: 'Invalid table name.',
    seat_not_found: 'Your seat has expired. Pick a table from the list.',
    seat_taken_over: 'You are now playing in another tab or window.',
    unknown: 'Something went wrong ({code}).'
  }
}
