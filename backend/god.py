"""Łaski bogów z Orlog (AC Valhalla). Koszty i wartości według
https://assassinscreed.fandom.com/wiki/Orlog

Każda łaska działa w jednej z faz walki:
  first  - przed zapłatą za pozostałe łaski (Kradzież Thryma obniża poziom łaski przeciwnika)
  before - przed atakami: zmienia kości i ich siłę
  after  - po atakach: obrażenia, leczenie, mana
W fazie kolejność ustala `order` (mniejsze najpierw), a przy remisie zaczyna gracz kierujący.
Teksty (opis łaski, wpis w dzienniku) tworzy frontend na podstawie `effect` i wartości.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Dict, List, Optional

from errors import GameError

if TYPE_CHECKING:
    from game import Game
    from player import Player

LEVELS = (1, 2, 3)

FIRST, BEFORE, AFTER = "first", "before", "after"

# łaski, które potrzebują dodatkowego wyboru gracza
NEEDS_AMOUNT = "amount"                 # ile HP poświęcić
NEEDS_OPPONENT_DICE = "opponent_dice"   # które kości przeciwnika
NEEDS_ANY_DICE = "any_dice"             # które kości (swoje i przeciwnika)

COMBAT_FACES = ("axe", "arrow", "helmet", "shield")


class FavorContext:
    """Wszystko, czego łaska potrzebuje w trakcie walki."""

    def __init__(self, game: Game, player: Player, opponent: Player, level: int,
                 choice: Dict, favors: Dict, stats: Dict) -> None:
        self.game = game
        self.player = player
        self.opponent = opponent
        self.level = level
        self.choice = choice or {}
        self.favors = favors   # imię gracza -> {"god", "level", ...}; Thrym obniża poziom przeciwnika
        self.stats = stats     # imię gracza -> blocked, axe_damage, damage_taken, spent

    def my(self, key: str) -> int:
        return self.stats[self.player.name][key]

    def theirs(self, key: str) -> int:
        return self.stats[self.opponent.name][key]


def _indexes(raw, size: int) -> List[int]:
    if raw is None:
        return []
    if not isinstance(raw, list) or any(type(i) is not int for i in raw) or len(set(raw)) != len(raw):
        raise GameError("invalid_targets")
    if any(i < 0 or i >= size for i in raw):
        raise GameError("invalid_targets")
    return list(raw)


class God:
    effect = ""
    phase = BEFORE
    order = 50
    needs: Optional[str] = None

    def __init__(self, name: str, values: List, mana_costs: List[int]) -> None:
        self.name = name
        self.values = values
        self.mana_costs = mana_costs

    def cost(self, level: int) -> int:
        return self.mana_costs[level - 1]

    def value(self, level: int):
        return self.values[level - 1]

    def validate_choice(self, player: Player, opponent: Player, level: int, choice: Dict) -> Dict:
        """Sprawdza dodatkowy wybór gracza i zwraca go w uporządkowanej postaci."""
        return {}

    def apply(self, ctx: FavorContext) -> Dict:
        raise NotImplementedError

    def return_data(self, level: Optional[int] = None) -> Dict[str, object]:
        return {"name": self.name,
                "effect": self.effect,
                "values": self.values,
                "mana_costs": self.mana_costs,
                "phase": self.phase,
                "needs": self.needs,
                "level": level}

    def __str__(self) -> str:
        return f"{self.name} ({self.effect} {self.values}, koszt {self.mana_costs})"


# ---------- po walce ----------

class ThorStrike(God):
    effect, phase, order = "thor_strike", AFTER, 10

    def apply(self, ctx):
        value = self.value(ctx.level)
        ctx.opponent.hp -= value
        ctx.stats[ctx.opponent.name]["damage_taken"] += value
        return {"target": ctx.opponent.name, "value": value, "hp": max(ctx.opponent.hp, 0)}


class SkuldClaim(God):
    effect, phase, order = "skuld_claim", AFTER, 20

    def apply(self, ctx):
        arrows = ctx.player.dice_stats["arrow"]
        destroyed = min(ctx.opponent.mana, self.value(ctx.level) * arrows)
        ctx.opponent.mana -= destroyed
        return {"target": ctx.opponent.name, "value": self.value(ctx.level), "arrows": arrows,
                "destroyed": destroyed, "left": ctx.opponent.mana}


class TyrPledge(God):
    effect, phase, order, needs = "tyr_pledge", AFTER, 30, NEEDS_AMOUNT

    def validate_choice(self, player, opponent, level, choice):
        return {"amount": _validate_amount(player, choice)}

    def apply(self, ctx):
        amount = max(0, min(ctx.choice.get("amount", 0), ctx.player.hp - 1))
        ctx.player.hp -= amount
        destroyed = min(ctx.opponent.mana, self.value(ctx.level) * amount)
        ctx.opponent.mana -= destroyed
        return {"target": ctx.opponent.name, "value": self.value(ctx.level), "sacrificed": amount,
                "destroyed": destroyed, "left": ctx.opponent.mana, "hp": ctx.player.hp}


class IdunRejuvenation(God):
    effect, phase, order = "idun_rejuvenation", AFTER, 40

    def apply(self, ctx):
        value = self.value(ctx.level)
        healed = ctx.player.heal(value)
        return {"value": value, "healed": healed, "hp": ctx.player.hp}


class HeimdallWatch(God):
    effect, phase, order = "heimdall_watch", AFTER, 41

    def apply(self, ctx):
        blocked = ctx.my("blocked")
        healed = ctx.player.heal(self.value(ctx.level) * blocked)
        return {"value": self.value(ctx.level), "blocked": blocked, "healed": healed, "hp": ctx.player.hp}


class HelGrip(God):
    effect, phase, order = "hel_grip", AFTER, 42

    def apply(self, ctx):
        damage = ctx.my("axe_damage")
        healed = ctx.player.heal(self.value(ctx.level) * damage)
        return {"value": self.value(ctx.level), "damage": damage, "healed": healed, "hp": ctx.player.hp}


class VarBond(God):
    effect, phase, order = "var_bond", AFTER, 43

    def apply(self, ctx):
        spent = ctx.theirs("spent")
        healed = ctx.player.heal(self.value(ctx.level) * spent)
        return {"value": self.value(ctx.level), "spent": spent, "healed": healed, "hp": ctx.player.hp}


class MimirWisdom(God):
    effect, phase, order = "mimir_wisdom", AFTER, 50

    def apply(self, ctx):
        damage = ctx.my("damage_taken")
        gained = self.value(ctx.level) * damage
        ctx.player.mana += gained
        return {"value": self.value(ctx.level), "damage": damage, "gained": gained, "total": ctx.player.mana}


class OdinSacrifice(God):
    effect, phase, order, needs = "odin_sacrifice", AFTER, 60, NEEDS_AMOUNT

    def validate_choice(self, player, opponent, level, choice):
        return {"amount": _validate_amount(player, choice)}

    def apply(self, ctx):
        amount = max(0, min(ctx.choice.get("amount", 0), ctx.player.hp - 1))
        ctx.player.hp -= amount
        gained = self.value(ctx.level) * amount
        ctx.player.mana += gained
        return {"value": self.value(ctx.level), "sacrificed": amount, "gained": gained,
                "hp": ctx.player.hp, "total": ctx.player.mana}


# ---------- przed walką ----------

class ThrymrTheft(God):
    effect, phase, order = "thrymr_theft", FIRST, 0

    def apply(self, ctx):
        target = ctx.favors.get(ctx.opponent.name)
        if target is None:
            return {"target": ctx.opponent.name, "target_god": None}
        old_level = target["level"]
        target["level"] = max(0, old_level - self.value(ctx.level))
        return {"target": ctx.opponent.name, "target_god": target["god"].name,
                "old_level": old_level, "new_level": target["level"]}


class FreyjaPlenty(God):
    effect, phase, order = "freyja_plenty", BEFORE, 10

    def apply(self, ctx):
        new_dice = [ctx.game.random_die() for _ in range(self.value(ctx.level))]
        ctx.player.saved_dice.extend(new_dice)
        gold = sum(1 for d in new_dice if d.gives_mana)
        ctx.player.mana += gold
        hands = sum(1 for d in new_dice if d.stat == "hand")
        stolen = min(hands, ctx.opponent.mana)
        ctx.opponent.mana -= stolen
        ctx.player.mana += stolen
        return {"value": self.value(ctx.level), "faces": [d.stat for d in new_dice],
                "mana": gold, "stolen": stolen, "total": ctx.player.mana}


class FriggSight(God):
    effect, phase, order, needs = "frigg_sight", BEFORE, 20, NEEDS_ANY_DICE

    def validate_choice(self, player, opponent, level, choice):
        targets = (choice or {}).get("targets") or {}
        if not isinstance(targets, dict):
            raise GameError("invalid_targets")
        own = _indexes(targets.get("own"), len(player.saved_dice))
        theirs = _indexes(targets.get("opponent"), len(opponent.saved_dice))
        if not 1 <= len(own) + len(theirs) <= self.value(level):
            raise GameError("targets_count", max=self.value(level))
        return {"targets": {"own": own, "opponent": theirs}}

    def apply(self, ctx):
        targets = ctx.choice.get("targets", {})
        for owner, key in ((ctx.player, "own"), (ctx.opponent, "opponent")):
            for i in targets.get(key, []):
                if i < len(owner.saved_dice):
                    owner.saved_dice[i] = ctx.game.random_die()
        return {"target": ctx.opponent.name, "own": len(targets.get("own", [])),
                "opponent": len(targets.get("opponent", []))}


class LokiTrick(God):
    effect, phase, order, needs = "loki_trick", BEFORE, 30, NEEDS_OPPONENT_DICE

    def validate_choice(self, player, opponent, level, choice):
        targets = (choice or {}).get("targets") or {}
        if not isinstance(targets, dict):
            raise GameError("invalid_targets")
        theirs = _indexes(targets.get("opponent"), len(opponent.saved_dice))
        if not 1 <= len(theirs) <= self.value(level):
            raise GameError("targets_count", max=self.value(level))
        return {"targets": {"opponent": theirs}}

    def apply(self, ctx):
        banned = []
        for i in ctx.choice.get("targets", {}).get("opponent", []):
            if i < len(ctx.opponent.saved_dice):
                die = ctx.opponent.saved_dice[i]
                die.banned = True
                banned.append(die.stat)
        return {"target": ctx.opponent.name, "banned": banned}


class BragiVerve(God):
    effect, phase, order = "bragi_verve", BEFORE, 35

    def apply(self, ctx):
        hands = ctx.player.dice_stats["hand"]
        gained = self.value(ctx.level) * hands
        ctx.player.mana += gained
        return {"value": self.value(ctx.level), "hands": hands, "gained": gained, "total": ctx.player.mana}


class VidarMight(God):
    effect, phase, order = "vidar_might", BEFORE, 40

    def apply(self, ctx):
        before = max(ctx.opponent.temp_stats["helmet"], 0)
        removed = min(before, self.value(ctx.level))
        ctx.opponent.add_bonus("helmet", -removed)
        return {"target": ctx.opponent.name, "value": self.value(ctx.level), "removed": removed}


class UllrAim(God):
    effect, phase, order = "ullr_aim", BEFORE, 41

    def apply(self, ctx):
        ctx.player.shield_ignore += self.value(ctx.level)
        return {"value": self.value(ctx.level)}


class BaldrInvulnerability(God):
    effect, phase, order = "baldr_invulnerability", BEFORE, 42

    def apply(self, ctx):
        stats = ctx.player.dice_stats
        value = self.value(ctx.level)
        helmets, shields = value * stats["helmet"], value * stats["shield"]
        ctx.player.add_bonus("helmet", helmets)
        ctx.player.add_bonus("shield", shields)
        return {"value": value, "helmets": helmets, "shields": shields}


class SkadiHunt(God):
    effect, phase, order = "skadi_hunt", BEFORE, 45

    def apply(self, ctx):
        added = self.value(ctx.level) * ctx.player.dice_stats["arrow"]
        ctx.player.add_bonus("arrow", added)
        return {"value": self.value(ctx.level), "added": added}


class FreyrGift(God):
    effect, phase, order = "freyr_gift", BEFORE, 46

    def apply(self, ctx):
        stats = ctx.player.dice_stats
        # ścianka, której jest najwięcej (przy remisie pierwsza w kolejności: topór, strzała, hełm, tarcza)
        best = max(COMBAT_FACES, key=lambda face: stats[face])
        if stats[best] == 0:
            return {"value": self.value(ctx.level), "stat": None}
        ctx.player.add_bonus(best, self.value(ctx.level))
        return {"value": self.value(ctx.level), "stat": best}


class BrunhildFury(God):
    effect, phase, order = "brunhild_fury", BEFORE, 49

    def apply(self, ctx):
        axes = max(ctx.player.temp_stats["axe"], 0)
        after = math.ceil(axes * self.value(ctx.level))
        ctx.player.add_bonus("axe", after - axes)
        return {"value": self.value(ctx.level), "before": axes, "after": after}


def _validate_amount(player: Player, choice: Dict) -> int:
    amount = (choice or {}).get("amount")
    if player.hp <= 1:
        raise GameError("not_enough_hp")
    if type(amount) is not int or not 1 <= amount <= player.hp - 1:
        raise GameError("invalid_amount", max=player.hp - 1)
    return amount


def god_factory() -> List[God]:
    return [
        ThorStrike("Thor", [2, 5, 8], [4, 8, 12]),
        IdunRejuvenation("Idun", [2, 4, 6], [4, 7, 10]),
        VidarMight("Vidar", [2, 4, 6], [2, 4, 6]),
        UllrAim("Ullr", [2, 3, 6], [2, 3, 4]),
        HeimdallWatch("Heimdall", [1, 2, 3], [4, 7, 10]),
        BaldrInvulnerability("Baldr", [1, 2, 3], [3, 6, 9]),
        BrunhildFury("Brunhild", [1.5, 2, 3], [6, 10, 18]),
        FreyrGift("Freyr", [2, 3, 4], [4, 6, 8]),
        HelGrip("Hel", [1, 2, 3], [6, 12, 18]),
        SkadiHunt("Skadi", [1, 2, 3], [6, 10, 14]),
        SkuldClaim("Skuld", [2, 3, 4], [4, 6, 8]),
        FriggSight("Frigg", [2, 3, 4], [2, 3, 4]),
        LokiTrick("Loki", [1, 2, 3], [3, 6, 9]),
        FreyjaPlenty("Freyja", [1, 2, 3], [2, 4, 6]),
        MimirWisdom("Mimir", [1, 2, 3], [3, 5, 7]),
        BragiVerve("Bragi", [2, 3, 4], [4, 8, 12]),
        OdinSacrifice("Odin", [3, 4, 5], [6, 8, 10]),
        VarBond("Var", [1, 2, 3], [10, 14, 18]),
        ThrymrTheft("Thrymr", [1, 2, 3], [3, 6, 9]),
        TyrPledge("Tyr", [2, 3, 4], [4, 6, 8]),
    ]
