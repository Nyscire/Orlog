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
  shield: ['tarcza', 'tarcze', 'tarcz']
}
// biernik obrony: "3 strzały na 1 tarczę"
const DEFENCE = {
  helmet: ['hełm', 'hełmy', 'hełmów'],
  shield: ['tarczę', 'tarcze', 'tarcz']
}
const BONUS_GENITIVE = { axe: 'toporów', arrow: 'strzał', helmet: 'hełmów', shield: 'tarcz' }
const BONUS_PART = { axe: 'do ataku', arrow: 'do ataku', helmet: 'do obrony', shield: 'do obrony' }
// "łaska Thora"
const GOD_GENITIVE = { Thor: 'Thora', Freya: 'Freyi', Heimdall: 'Heimdalla', Loki: 'Lokiego', Odin: 'Odyna' }

const count = (n, forms) => `${n} ${plural(n, forms)}`
const damage = n => `${n} ${plural(n, ['obrażenie', 'obrażenia', 'obrażeń'])}`
const gen = name => GOD_GENITIVE[name] || name

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
    manaTitle: 'Mana: za nią kupujesz łaski bogów. Mana z odłożonych kości dochodzi po fazie rzutów.',
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
    mana: { name: 'Mana', desc: 'Daje 1 manę. Manę wydajesz na łaski bogów.' },
    manaBorder: 'Złota obwódka: kość daje dodatkowo 1 manę.',
    manaBorderName: 'Złota obwódka',
    manaBorderLegend: 'Kość daje dodatkowo 1 manę, niezależnie od symbolu.',
    extraMana: 'daje dodatkowo 1 manę',
    // "Atak: 2 topory, 1 strzała · Obrona: 1 hełm · Mana: +3"
    summary: dice => {
      const { counts, mana } = faceCounts(dice)
      const attack = ['axe', 'arrow'].filter(f => counts[f]).map(f => count(counts[f], FACES[f]))
      const defence = ['helmet', 'shield'].filter(f => counts[f]).map(f => count(counts[f], FACES[f]))
      const parts = []
      if (attack.length) parts.push(`Atak: ${attack.join(', ')}`)
      if (defence.length) parts.push(`Obrona: ${defence.join(', ')}`)
      if (mana) parts.push(`Mana: +${mana}`)
      return parts.join(' · ')
    }
  },

  gods: {
    choose: 'Wybierz',
    level: 'Poziom {level}',
    levelText: 'Poziom {level}: {text}',
    costs: god => `Koszt many: ${god.mana_costs.join(' / ')}`,
    describe: god => {
      const v = (god.values || []).join(' / ')
      if (god.effect === 'damage') return `Zadaje przeciwnikowi ${v} obrażeń.`
      if (god.effect === 'heal') return `Przywraca ci ${v} HP.`
      if (god.effect === 'bonus') return `Dodaje ${v} ${FACES[god.stat]?.[1] || god.stat} ${BONUS_PART[god.stat] || ''} w tej rundzie.`
      return ''
    },
    levelEffect: ({ god, level }) => {
      const value = god.values?.[level - 1]
      const cost = god.mana_costs?.[level - 1]
      if (god.effect === 'damage') return `${damage(value)} (${cost} many)`
      if (god.effect === 'heal') return `+${value} HP (${cost} many)`
      if (god.effect === 'bonus') return `+${count(value, FACES[god.stat] || [god.stat, god.stat, god.stat])} (${cost} many)`
      return `${cost} many`
    }
  },

  log: {
    title: 'Przebieg gry',
    empty: 'Tu pojawią się ruchy graczy i wyniki walk.',
    round: 'Runda {n}',
    events: {
      round_start: p => `Zaczyna ${p.leader}`,
      dice_summary: p => {
        const parts = ['axe', 'arrow', 'helmet', 'shield'].filter(f => p.counts?.[f]).map(f => count(p.counts[f], FACES[f]))
        let text = `${p.player}: ${parts.length ? parts.join(', ') : 'bez broni i obrony'}.`
        if (p.mana) text += ` Mana z kości: ${p.mana}.`
        return text
      },
      mana_collected: p => `Mana z kości trafia do puli: ${p.gains.map(g => `${g.player} +${g.gained} (razem ${g.total})`).join(', ')}.`,
      god_chosen: p => `${p.player} wybiera łaskę ${gen(p.god)}, poziom ${p.level} (koszt ${p.cost} many).`,
      god_skipped: p => `${p.player} nie korzysta z łaski w tej rundzie.`,
      god_effect: p => {
        const head = `${p.player} używa łaski ${gen(p.god)}:`
        if (p.effect === 'damage') return `${head} ${p.target} traci ${p.value} HP i ma teraz ${p.hp}.`
        if (p.effect === 'heal') return `${head} odzyskuje ${p.value} HP i ma teraz ${p.hp}.`
        if (p.effect === 'bonus') return `${head} +${p.value} do ${BONUS_GENITIVE[p.stat] || p.stat} w tej rundzie.`
        return `${head} ${p.effect}.`
      },
      god_failed: p => `${p.player} nie może użyć łaski ${gen(p.god)}: za mało many (${p.mana} z ${p.cost}).`,
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
      { title: 'Łaski bogów.', text: 'Każdy może kupić łaskę jednego ze swoich bogów albo ją pominąć. Łaska kosztuje manę, a wyższy poziom daje silniejszy efekt.' },
      { title: 'Walka.', text: 'Działają łaski, a potem atakuje gracz, który zaczynał rundę, i po nim drugi. W następnej rundzie zaczyna drugi gracz.' }
    ],
    diceTitle: 'Kości',
    attackTitle: 'Jak liczy się atak',
    attackText: 'Każda strzała zadaje 1 obrażenie, chyba że zablokuje ją tarcza. Każdy topór zadaje 1 obrażenie, chyba że zablokuje go hełm. Na przykład 3 strzały na 1 tarczę to 2 obrażenia.',
    manaTitle: 'Mana i bogowie',
    manaText: 'Mana z odłożonych kości trafia do puli po fazie rzutów, a niewydana zostaje na kolejne rundy. Przed grą wybierasz do 3 bogów. Po najechaniu na kartę boga zobaczysz, co robi, a po wybraniu poziomu: jego efekt i koszt.',
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
      forest: 'Leśny mech'
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
    join_first: 'Najpierw dołącz do gry.',
    already_playing_as: 'Grasz już jako {name}.',
    player_left: '{name} kończy partię. Możesz zacząć nową grę.',
    unknown: 'Coś poszło nie tak ({code}).'
  }
}
