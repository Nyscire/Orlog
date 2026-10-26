// Teksty po polsku. Funkcje dostają parametry i zajmują się odmianą.

function plural(n, [one, few, many]) {
  if (n === 1) return one
  if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return few
  return many
}

const FACES = {
  axe: ['topór', 'topory', 'toporów'],
  arrow: ['strzała', 'strzały', 'strzał'],
  helmet: ['hełm', 'hełmy', 'hełmów'],
  shield: ['tarcza', 'tarcze', 'tarcz'],
  hand: ['ręka', 'ręce', 'rąk']
}
// biernik obrony: "3 strzały na 1 tarczę"
const DEFENCE = {
  helmet: ['hełm', 'hełmy', 'hełmów'],
  shield: ['tarczę', 'tarcze', 'tarcz']
}
const DICE = ['kość', 'kości', 'kości']
const MANA = n => `${n} many`
const HP = n => `${n} HP`

// polskie imiona bogów (pozostałe zostają jak w grze)
const GOD_NAMES = { Odin: 'Odyn', Freyja: 'Freja', Brunhild: 'Brunhilda', Thrymr: 'Thrym', Idun: 'Idunn' }

const count = (n, forms) => `${n} ${plural(n, forms)}`
const damage = n => `${n} ${plural(n, ['obrażenie', 'obrażenia', 'obrażeń'])}`
const godName = name => GOD_NAMES[name] || name
const num = n => String(n).replace('.', ',')
const SLASH = '\u00a0/\u00a0'   // "2 / 5 / 8" bez łamania wiersza w środku
const faceList = faces => faces.map(f => FACES[f]?.[0] || f).join(', ')

// Łaski: nazwa, opis (wartości wszystkich poziomów), efekt jednego poziomu i wpis w dzienniku
const FAVORS = {
  thor_strike: {
    name: 'Uderzenie Thora',
    desc: v => `Po walce zadaje przeciwnikowi ${v} obrażeń.`,
    level: x => damage(x),
    log: p => `${p.target} traci ${HP(p.value)}, zostaje ${p.hp}.`
  },
  idun_rejuvenation: {
    name: 'Odmłodzenie Idunn',
    desc: v => `Po walce leczy cię o ${v} HP.`,
    level: x => `+${HP(x)}`,
    log: p => `+${HP(p.healed)}, ma teraz ${p.hp}.`
  },
  vidar_might: {
    name: 'Potęga Vidara',
    desc: v => `Przed walką zdejmuje przeciwnikowi ${v} hełmów.`,
    level: x => `−${count(x, FACES.helmet)} przeciwnika`,
    log: p => (p.removed ? `${p.target} traci ${count(p.removed, FACES.helmet)}.` : `${p.target} nie ma hełmów do zdjęcia.`)
  },
  ullr_aim: {
    name: 'Celność Ullra',
    desc: v => `Twoje strzały omijają ${v} tarcz przeciwnika.`,
    level: x => `strzały omijają ${count(x, DEFENCE.shield)}`,
    log: p => `strzały omijają ${count(p.value, DEFENCE.shield)} przeciwnika.`
  },
  heimdall_watch: {
    name: 'Czujność Heimdalla',
    desc: v => `Po walce +${v} HP za każdy zablokowany atak.`,
    level: x => `+${HP(x)} za każdy blok`,
    log: p => `zablokowane ataki: ${p.blocked}, +${HP(p.healed)}, ma teraz ${p.hp}.`
  },
  baldr_invulnerability: {
    name: 'Niezniszczalność Baldra',
    desc: v => `Każdy hełm i tarcza na kościach daje dodatkowo ${v}.`,
    level: x => `+${x} za każdy hełm i tarczę`,
    log: p => `obrona +${count(p.helmets, FACES.helmet)}, +${count(p.shields, FACES.shield)}.`
  },
  brunhild_fury: {
    name: 'Furia Brunhildy',
    desc: v => `Mnoży topory ×${v} (w górę).`,
    level: x => `topory ×${num(x)}`,
    log: p => `topory: ${p.before} → ${p.after}.`
  },
  freyr_gift: {
    name: 'Dar Freyra',
    desc: v => `+${v} do symbolu, którego masz najwięcej (topór, strzała, hełm, tarcza).`,
    level: x => `+${x} do najczęstszego symbolu`,
    log: p => (p.stat ? `+${count(p.value, FACES[p.stat])}.` : 'brak toporów, strzał, hełmów i tarcz, łaska nic nie daje.')
  },
  hel_grip: {
    name: 'Uścisk Hel',
    desc: v => `Po walce +${v} HP za każde obrażenie od twoich toporów.`,
    level: x => `+${HP(x)} za obrażenie od topora`,
    log: p => `obrażenia od toporów: ${p.damage}, +${HP(p.healed)}, ma teraz ${p.hp}.`
  },
  skadi_hunt: {
    name: 'Łowy Skadi',
    desc: v => `Każda strzała na kościach daje dodatkowo ${v}.`,
    level: x => `+${x} do każdej strzały`,
    log: p => `+${count(p.added, FACES.arrow)}.`
  },
  skuld_claim: {
    name: 'Roszczenie Skuld',
    desc: v => `Po walce przeciwnik traci ${v} many za każdą twoją strzałę.`,
    level: x => `−${MANA(x)} przeciwnika za strzałę`,
    log: p => `${p.target} traci ${MANA(p.destroyed)}, zostaje ${p.left}.`
  },
  frigg_sight: {
    name: 'Wizja Frigg',
    desc: v => `Przed walką przerzuca ${v} wskazane kości, twoje lub przeciwnika.`,
    level: x => `przerzut do ${count(x, DICE)}`,
    log: p => `przerzucone kości: własne ${p.own}, przeciwnika ${p.opponent}.`
  },
  loki_trick: {
    name: 'Podstęp Lokiego',
    desc: v => `Blokuje ${v} wskazane kości przeciwnika na tę rundę.`,
    level: x => `blokuje ${count(x, DICE)} przeciwnika`,
    log: p => (p.banned.length ? `${p.target} traci w tej rundzie: ${faceList(p.banned)}.` : 'nie ma czego zablokować.')
  },
  freyja_plenty: {
    name: 'Obfitość Frei',
    desc: v => `Przed walką dorzucasz ${v} dodatkowe kości.`,
    level: x => `+${count(x, DICE)}`,
    log: p => {
      let text = `dodatkowe kości: ${faceList(p.faces)}.`
      if (p.mana) text += ` Mana z obwódek: +${p.mana}.`
      if (p.stolen) text += ` Ręce kradną ${MANA(p.stolen)}.`
      return text
    }
  },
  mimir_wisdom: {
    name: 'Mądrość Mimira',
    desc: v => `Po walce +${v} many za każde otrzymane obrażenie.`,
    level: x => `+${MANA(x)} za obrażenie`,
    log: p => `otrzymane obrażenia: ${p.damage}, +${MANA(p.gained)} (razem ${p.total}).`
  },
  bragi_verve: {
    name: 'Zapał Bragiego',
    desc: v => `+${v} many za każdą rękę na kościach.`,
    level: x => `+${MANA(x)} za rękę`,
    log: p => `ręce: ${p.hands}, +${MANA(p.gained)} (razem ${p.total}).`
  },
  odin_sacrifice: {
    name: 'Ofiara Odyna',
    desc: v => `Po walce poświęcasz wybrane HP, za każde +${v} many.`,
    level: x => `${MANA(x)} za 1 HP`,
    log: p => `poświęca ${HP(p.sacrificed)} i dostaje ${MANA(p.gained)} (HP: ${p.hp}, mana: ${p.total}).`
  },
  var_bond: {
    name: 'Przysięga Var',
    desc: v => `Po walce +${v} HP za każdą manę wydaną przez przeciwnika.`,
    level: x => `+${HP(x)} za manę przeciwnika`,
    log: p => `przeciwnik wydał ${MANA(p.spent)}, +${HP(p.healed)}, ma teraz ${p.hp}.`
  },
  thrymr_theft: {
    name: 'Kradzież Thryma',
    desc: v => `Obniża łaskę przeciwnika o ${v} poziomy. Wydana na nią mana przepada.`,
    level: x => `łaska przeciwnika −${x} ${plural(x, ['poziom', 'poziomy', 'poziomów'])}`,
    log: p => {
      if (!p.target_god) return `${p.target} nie wybrał łaski, nie ma czego obniżyć.`
      if (!p.new_level) return `${p.target}: ${favorByGod(p.target_god)} przepada.`
      return `${p.target}: ${favorByGod(p.target_god)} spada z poziomu ${p.old_level} na ${p.new_level}.`
    }
  },
  tyr_pledge: {
    name: 'Zastaw Tyra',
    desc: v => `Po walce poświęcasz wybrane HP, za każde przeciwnik traci ${v} many.`,
    level: x => `−${MANA(x)} przeciwnika za 1 HP`,
    log: p => `poświęca ${HP(p.sacrificed)}, ${p.target} traci ${MANA(p.destroyed)} (zostaje ${p.left}).`
  }
}
const favor = effect => FAVORS[effect] || { name: effect, desc: () => '', level: () => '', log: () => '' }
// nazwa łaski po imieniu boga, gdy nie znamy efektu (np. w starszych wpisach dziennika)
const favorByGod = name => {
  const key = Object.keys(FAVORS).find(k => k.startsWith(name.toLowerCase() + '_'))
  return key ? FAVORS[key].name : godName(name)
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

export const pl = {
  menu: {
    subtitle: 'Gra w kości dla dwóch wojowników',
    yourName: 'Twoje imię',
    namePlaceholder: 'np. Eivor',
    godsLabel: 'Bogowie, których zabierasz do gry',
    godsHint: 'Ich łaski będziesz mógł wykupić maną w trakcie partii.',
    loadingGods: 'Wczytuję bogów z serwera…',
    costs: 'Mana: {costs}',
    join: 'Dołącz do gry',
    playWith: 'Zagraj z: {names}',
    gameInProgress: 'Trwa partia: {players}. Jeśli to Ty, wpisz to samo imię, żeby wrócić do gry.',
    and: ' i ',
    waitingTitle: 'Czekamy na drugiego gracza',
    playingAs: 'Grasz jako',
    withGods: 'bogowie: {gods}.',
    waitingHint: 'Drugi gracz otwiera tę samą stronę i wpisuje swoje imię.',
    changeChoice: 'Zmień imię albo bogów',
    howToPlay: 'Jak grać?',
    settings: 'Ustawienia',
    status: {
      offline: 'Brak połączenia z serwerem. Sprawdź, czy backend działa (python main.py).',
      joined: 'Połączono z serwerem',
      inProgress: 'Połączono · na serwerze trwa partia',
      waiting: 'Połączono · na rywala czeka: {names}',
      empty: 'Połączono · nikt jeszcze nie czeka'
    }
  },

  board: {
    selfOffline: 'Utracono połączenie z serwerem. Próbuję połączyć ponownie…',
    opponentOffline: 'jest offline. Gra poczeka, aż przeciwnik wróci pod tym samym imieniem. Możesz też zakończyć partię.',
    endGame: 'Zakończ partię'
  },

  stage: {
    waiting: 'Oczekiwanie na graczy',
    dice: 'Faza kości',
    gods: 'Wybór bogów',
    battle: 'Walka!',
    finished: 'Koniec gry',
    unknown: 'Nieznana faza'
  },

  neutral: {
    round: 'Runda {n}',
    yourTurn: 'Twoja tura',
    turnOf: 'Ruch:',
    howToPlay: 'Jak grać?',
    settings: 'Ustawienia',
    leave: 'Opuść grę',
    leaveConfirm: 'Zakończyć partię dla obu graczy?',
    leaveYes: 'Tak, wyjdź',
    no: 'Nie',
    yourSaved: 'Twoje odłożone kości',
    opponentSaved: 'Odłożone kości przeciwnika',
    nothingSaved: 'Jeszcze nic nie odłożono',
    youWin: 'Wygrywasz!',
    winnerIs: 'Wygrywa {name}',
    newGame: 'Nowa partia',
    hint: {
      waiting: 'Czekamy na drugiego gracza…',
      opponentRolling: '{name} rzuca kośćmi…',
      lastThrow: 'Ostatni rzut: wszystkie wylosowane kości zostaną zachowane.',
      pickDice: 'Kliknij kości, które chcesz zatrzymać, i potwierdź. Pozostałe rzucisz ponownie.',
      opponentChoosing: '{name} wybiera łaskę boga…',
      pickGod: 'Wybierz poziom łaski i kliknij „Wybierz” albo pomiń łaskę. Dostępna mana: {mana}.'
    }
  },

  player: {
    yourTurn: 'Twoja tura',
    rollsLeft: 'Pozostałe rzuty: {n}',
    rollsTitle: 'Ile razy możesz jeszcze rzucić w tej rundzie',
    pickDice: 'Wybierz kości',
    yourDice: 'Twoje kości',
    selected: 'Wybrano: {n}',
    confirmLast: 'Zachowaj wszystkie (ostatni rzut)',
    confirmSelected: 'Zatwierdź wybrane ({n})',
    rerollAll: 'Rzuć ponownie wszystkimi',
    pickGod: 'Wybierz boga',
    yourGods: 'Twoi bogowie',
    chosen: 'Wybrany: {god}',
    skipGod: 'Pomiń łaskę w tej rundzie'
  },

  stats: {
    hp: 'HP',
    hpTitle: 'Życie: {hp} z {max}. Kto spadnie do zera, przegrywa.',
    mana: 'Mana',
    manaTitle: 'Mana: za nią kupujesz łaski bogów. Po fazie rzutów złote obwódki dają manę, a ręce kradną ją przeciwnikowi.',
    fromDice: '+{n} z kości'
  },

  opponent: {
    roll: 'Rzut przeciwnika'
  },

  dice: {
    axe: { name: 'Topór', desc: 'Atak wręcz: 1 obrażenie. Blokuje go hełm przeciwnika.' },
    arrow: { name: 'Strzała', desc: 'Atak z dystansu: 1 obrażenie. Blokuje ją tarcza przeciwnika.' },
    helmet: { name: 'Hełm', desc: 'Obrona: blokuje 1 topór przeciwnika.' },
    shield: { name: 'Tarcza', desc: 'Obrona: blokuje 1 strzałę przeciwnika.' },
    hand: { name: 'Ręka', desc: 'Kradnie przeciwnikowi 1 manę, jeśli ją ma.' },
    manaBorder: 'Złota obwódka: kość daje 1 manę.',
    manaBorderName: 'Złota obwódka',
    manaBorderLegend: 'Kość daje 1 manę, niezależnie od symbolu.',
    extraMana: 'daje 1 manę',
    // "2 topory, 1 strzała · 1 hełm · 2 ręce · +3 many"
    summary: dice => {
      const { counts, mana } = faceCounts(dice)
      const group = faces => faces.filter(f => counts[f]).map(f => count(counts[f], FACES[f])).join(', ')
      const parts = [group(['axe', 'arrow']), group(['helmet', 'shield']), group(['hand'])].filter(Boolean)
      if (mana) parts.push(`+${MANA(mana)}`)
      return parts.join(' · ')
    }
  },

  gods: {
    choose: 'Wybierz',
    level: 'Poziom {level}',
    levelText: 'Poziom {level}: {text}',
    name: god => godName(god.name),
    favor: god => favor(god.effect).name,
    costs: god => `Koszt many: ${god.mana_costs.join(SLASH)}`,
    describe: god => favor(god.effect).desc((god.values || []).map(num).join(SLASH)),
    levelEffect: ({ god, level }) => {
      const value = god.values?.[level - 1]
      const cost = god.mana_costs?.[level - 1]
      return `${favor(god.effect).level(value)} (${MANA(cost)})`
    },
    phase: {
      first: 'Na początku walki',
      before: 'Przed walką',
      after: 'Po walce'
    },
    // dodatkowy wybór przy łasce
    sacrifice: 'Poświęć',
    sacrificed: 'Poświęca {n} HP',
    less: 'Mniej',
    more: 'Więcej',
    sacrificeResult: ({ god, level, amount }) => {
      const value = god.values?.[level - 1] || 0
      return god.effect === 'tyr_pledge'
        ? `−${MANA(value * amount)} przeciwnika`
        : `+${MANA(value * amount)}`
    },
    pickTargets: ({ picked, max }) => `Wskaż kości na stole: ${picked} z ${max}`,
    pickTargetsHint: ({ god, max, any }) => any
      ? `${favor(god.effect).name}: kliknij na stole do ${count(max, DICE)} (twoje albo przeciwnika), które chcesz przerzucić.`
      : `${favor(god.effect).name}: kliknij na stole do ${count(max, DICE)} przeciwnika, które chcesz zablokować.`
  },

  log: {
    title: 'Przebieg gry',
    empty: 'Tu pojawią się ruchy graczy i wyniki walk.',
    round: 'Runda {n}',
    events: {
      round_start: p => `Zaczyna ${p.leader}`,
      dice_summary: p => {
        const parts = ['axe', 'arrow', 'helmet', 'shield', 'hand'].filter(f => p.counts?.[f]).map(f => count(p.counts[f], FACES[f]))
        let text = `${p.player}: ${parts.length ? parts.join(', ') : 'bez broni i obrony'}.`
        if (p.mana) text += ` Złote obwódki: ${p.mana}.`
        return text
      },
      mana_collected: p => `Mana z obwódek trafia do puli: ${p.gains.map(g => `${g.player} +${g.gained} (razem ${g.total})`).join(', ')}.`,
      mana_stolen: p => (p.amount
        ? `${p.thief} kradnie ${MANA(p.amount)} (${count(p.hands, FACES.hand)}). Mana: ${p.thief} ${p.thief_total}, ${p.victim} ${p.victim_total}.`
        : `${p.thief}: ${count(p.hands, FACES.hand)} bez łupu, ${p.victim} nie ma many.`),
      god_chosen: p => {
        let text = `${p.player} wybiera łaskę: ${favorByGod(p.god)}, poziom ${p.level} (koszt ${MANA(p.cost)}).`
        if (p.amount) text += ` Poświęci ${HP(p.amount)}.`
        if (p.targets) {
          const n = (p.targets.own || []).length + (p.targets.opponent || []).length
          text += ` Wybrane kości: ${n}.`
        }
        return text
      },
      god_skipped: p => `${p.player} nie korzysta z łaski w tej rundzie.`,
      god_effect: p => `${p.player} · ${favor(p.effect).name}: ${favor(p.effect).log(p)}`,
      god_failed: p => `${p.player} · ${favorByGod(p.god)}: za mało many (${p.mana} z ${p.cost}), łaska nie działa.`,
      god_cancelled: p => `${p.player} · ${favorByGod(p.god)}: łaska przepada przez Kradzież Thryma, wydana mana (${p.cost}) nie wraca.`,
      attack: p => {
        const parts = []
        if (p.arrow) parts.push(`${count(p.arrow, FACES.arrow)} na ${count(p.shield, DEFENCE.shield)}`)
        if (p.axe) parts.push(`${count(p.axe, FACES.axe)} na ${count(p.helmet, DEFENCE.helmet)}`)
        if (!parts.length) return `${p.attacker} nie atakuje: nie ma strzał ani toporów.`
        const outcome = p.dmg
          ? `Zadaje ${damage(p.dmg)}, ${p.defender} ma teraz ${p.hp} HP.`
          : `Obrona blokuje wszystko, ${p.defender} ma nadal ${p.hp} HP.`
        return `${p.attacker} atakuje: ${parts.join(', ')}. ${outcome}`
      },
      win: p => `Koniec gry. Wygrywa ${p.winner}.`
    }
  },

  help: {
    title: 'Jak grać w Orlog',
    lead: 'Wygrywa ten, kto pierwszy sprowadzi życie przeciwnika do zera. Każdy zaczyna z 21 HP.',
    roundTitle: 'Przebieg rundy',
    steps: [
      { title: 'Rzuty kośćmi.', text: 'Gracze rzucają na zmianę sześcioma kośćmi. Po każdym rzucie zaznaczasz kości, które chcesz zatrzymać, a resztę rzucasz ponownie. Masz 3 rzuty, w ostatnim zostają wszystkie kości.' },
      { title: 'Mana.', text: 'Każda złota obwódka daje 1 manę, a każda ręka kradnie przeciwnikowi 1 manę, jeśli ją ma.' },
      { title: 'Łaski bogów.', text: 'Każdy może kupić łaskę jednego ze swoich bogów albo ją pominąć. Wyższy poziom kosztuje więcej i daje silniejszy efekt.' },
      { title: 'Walka.', text: 'Najpierw działają łaski „przed walką”, potem atakuje gracz, który zaczynał rundę, i po nim drugi, a na końcu łaski „po walce”. W następnej rundzie zaczyna drugi gracz.' }
    ],
    diceTitle: 'Kości',
    attackTitle: 'Jak liczy się atak',
    attackText: 'Każda strzała zadaje 1 obrażenie, chyba że zablokuje ją tarcza. Każdy topór zadaje 1 obrażenie, chyba że zablokuje go hełm. Na przykład 3 strzały na 1 tarczę to 2 obrażenia.',
    manaTitle: 'Mana i bogowie',
    manaText: 'Mana z kości trafia do puli po fazie rzutów, a niewydana zostaje na kolejne rundy. Przed grą wybierasz do 3 z 20 bogów. Po najechaniu na kartę boga zobaczysz, co robi, a po wybraniu poziomu: jego efekt i koszt. Kilka łask wymaga dodatkowego wyboru: Frigg i Loki wskazują kości na stole, a Odyn i Tyr ile HP poświęcić.',
    ok: 'Rozumiem',
    close: 'Zamknij'
  },

  settings: {
    title: 'Ustawienia',
    language: 'Język',
    theme: 'Kolory',
    font: 'Czcionka',
    size: 'Wielkość tekstu',
    done: 'Gotowe',
    sample: 'Topór, strzała i tarcza',
    themes: {
      classic: 'Drewno i złoto',
      frost: 'Mroźna północ',
      ember: 'Popiół i krew',
      forest: 'Leśny mech',
      night: 'Noc polarna',
      abyss: 'Otchłań Hel'
    },
    fonts: {
      classic: 'Klasyczna',
      medieval: 'Średniowieczna',
      readable: 'Czytelna'
    },
    sizes: {
      normal: 'Normalna',
      large: 'Duża'
    }
  },

  errors: {
    game_finished: 'Gra już się zakończyła.',
    wrong_stage: 'To nie jest ta faza gry.',
    not_your_turn: 'To nie jest Twoja tura.',
    no_opponent: 'Brak przeciwnika.',
    invalid_gods: 'Nieprawidłowy wybór bogów.',
    duplicate_gods: 'Każdego boga można wybrać tylko raz.',
    gods_count: 'Wybierz od 1 do {max} bogów.',
    unknown_god: 'Nie ma boga {god}.',
    name_required: 'Podaj nazwę gracza.',
    name_too_long: 'Nazwa może mieć najwyżej {max} znaków.',
    name_taken: 'Ta nazwa jest już zajęta.',
    game_full: 'Gra jest już pełna.',
    cannot_start: 'Gra nie może się jeszcze zacząć.',
    game_in_progress: 'Partia jeszcze trwa.',
    invalid_dice: 'Nieprawidłowy wybór kości.',
    invalid_level: 'Poziom łaski musi wynosić 1, 2 lub 3.',
    not_enough_mana: 'Za mało many: {god} na poziomie {level} kosztuje {cost}, a masz {mana}.',
    invalid_amount: 'Możesz poświęcić od 1 do {max} HP.',
    not_enough_hp: 'Masz za mało HP, żeby coś poświęcić.',
    invalid_targets: 'Nieprawidłowy wybór kości dla łaski.',
    targets_count: 'Wskaż od 1 do {max} kości.',
    join_first: 'Najpierw dołącz do gry.',
    already_playing_as: 'Grasz już jako {name}.',
    player_left: '{name} kończy partię. Możesz zacząć nową grę.',
    unknown: 'Coś poszło nie tak ({code}).'
  }
}
