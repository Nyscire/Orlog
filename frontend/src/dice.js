// Opisy kości używane w podpowiedziach, legendzie i podsumowaniach

export const DICE_INFO = {
  axe: {
    name: 'Topór',
    forms: ['topór', 'topory', 'toporów'],
    desc: 'Atak wręcz: 1 obrażenie. Blokuje go hełm przeciwnika.'
  },
  arrow: {
    name: 'Strzała',
    forms: ['strzała', 'strzały', 'strzał'],
    desc: 'Atak z dystansu: 1 obrażenie. Blokuje ją tarcza przeciwnika.'
  },
  helmet: {
    name: 'Hełm',
    forms: ['hełm', 'hełmy', 'hełmów'],
    desc: 'Obrona: blokuje 1 topór przeciwnika.'
  },
  shield: {
    name: 'Tarcza',
    forms: ['tarcza', 'tarcze', 'tarcz'],
    desc: 'Obrona: blokuje 1 strzałę przeciwnika.'
  },
  mana: {
    name: 'Mana',
    forms: ['mana', 'many', 'many'],
    desc: 'Daje 1 manę. Manę wydajesz na łaski bogów.'
  }
}

export const FACE_ORDER = ['axe', 'arrow', 'helmet', 'shield', 'mana']

export const MANA_BORDER_DESC = 'Złota obwódka: kość daje dodatkowo 1 manę.'

export function plural(n, [one, few, many]) {
  if (n === 1) return one
  if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return few
  return many
}

function countText(n, face) {
  return `${n} ${plural(n, DICE_INFO[face].forms)}`
}

// "Atak: 2 topory, 1 strzała · Obrona: 1 hełm · Mana: +3"
export function diceSummary(dice) {
  if (!dice || dice.length === 0) return ''
  const counts = { axe: 0, arrow: 0, helmet: 0, shield: 0 }
  let mana = 0
  for (const die of dice) {
    if (die.stat in counts) counts[die.stat] += 1
    if (die.stat === 'mana') mana += 1
    if (die.gives_mana) mana += 1
  }
  const attack = ['axe', 'arrow'].filter(f => counts[f]).map(f => countText(counts[f], f))
  const defence = ['helmet', 'shield'].filter(f => counts[f]).map(f => countText(counts[f], f))
  const parts = []
  if (attack.length) parts.push(`Atak: ${attack.join(', ')}`)
  if (defence.length) parts.push(`Obrona: ${defence.join(', ')}`)
  if (mana) parts.push(`Mana: +${mana}`)
  return parts.join(' · ')
}
