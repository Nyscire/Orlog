"""Zapis rozegranych partii i statystyki graczy: bilans, historia, bogowie, ranking.

Partia trafia do bazy, jeśli grał w niej choć jeden zalogowany gracz.
Ranking (Elo) zmieniają tylko partie rankingowe, w których grają same konta.
"""
from __future__ import annotations

import json
import time
from typing import Callable, Dict, List, Optional

from db import Database


def elo_change(winner: int, loser: int, k: int) -> int:
    """O ile punktów zmienia się ranking po partii (wygrany +, przegrany -)."""
    expected = 1 / (1 + 10 ** ((loser - winner) / 400))
    return max(1, round(k * (1 - expected)))


class Stats:
    K = 32
    HISTORY_PAGE = 20
    RANKING_SIZE = 50

    def __init__(self, db: Database, clock: Callable[[], float] = time.time) -> None:
        self.db = db
        self.clock = clock

    # ---------- zapis ----------

    def record_match(self, result: Dict) -> Dict[str, Dict[str, int]]:
        """Zapisuje skończoną partię.

        result: {"ranked": bool, "rounds": int, "forfeit": bool,
                 "players": [{"name", "user_id", "won", "hp", "gods"}, ...]}
        Zwraca zmiany rankingu: {imię: {"before": ..., "after": ...}} (puste poza rankingowymi).
        """
        players = result["players"]
        if not any(p.get("user_id") for p in players):
            return {}
        ranked = bool(result.get("ranked")) and all(p.get("user_id") for p in players) and len(players) == 2
        changes: Dict[str, Dict[str, int]] = {}
        with self.db.transaction() as conn:
            if ranked:
                ratings = {p["name"]: conn.execute("SELECT rating FROM users WHERE id = ?",
                                                   (p["user_id"],)).fetchone()["rating"] for p in players}
                winner = next(p for p in players if p["won"])
                loser = next(p for p in players if not p["won"])
                delta = elo_change(ratings[winner["name"]], ratings[loser["name"]], self.K)
                for player, sign in ((winner, 1), (loser, -1)):
                    before = ratings[player["name"]]
                    changes[player["name"]] = {"before": before, "after": before + sign * delta}
                    conn.execute("UPDATE users SET rating = ? WHERE id = ?",
                                 (before + sign * delta, player["user_id"]))
            cursor = conn.execute("INSERT INTO matches (ranked, rounds, forfeit, finished_at) VALUES (?, ?, ?, ?)",
                                  (int(ranked), int(result.get("rounds") or 0), int(bool(result.get("forfeit"))),
                                   self.clock()))
            match_id = cursor.lastrowid
            for seat, player in enumerate(players):
                change = changes.get(player["name"], {})
                conn.execute(
                    "INSERT INTO match_players (match_id, seat, user_id, name, won, hp, gods, rating_before, rating_after) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (match_id, seat, player.get("user_id"), player["name"], int(bool(player["won"])),
                     max(int(player.get("hp") or 0), 0), json.dumps(list(player.get("gods") or [])),
                     change.get("before"), change.get("after")))
        return changes

    # ---------- odczyt ----------

    def _user(self, login) -> Optional[object]:
        if not isinstance(login, str) or not login.strip():
            return None
        return self.db.one("SELECT id, login, rating, created_at FROM users WHERE login_key = ?",
                           (login.strip().casefold(),))

    def position(self, user_id: int, rating: int) -> Optional[int]:
        """Miejsce w rankingu (tylko gracze z co najmniej jedną partią rankingową)."""
        if not self._has_ranked(user_id):
            return None
        row = self.db.one(
            "SELECT COUNT(*) FROM users u WHERE u.rating > ? AND EXISTS ("
            " SELECT 1 FROM match_players mp JOIN matches m ON m.id = mp.match_id"
            " WHERE mp.user_id = u.id AND m.ranked = 1)", (rating,))
        return row[0] + 1

    def _has_ranked(self, user_id: int) -> bool:
        return self.db.one("SELECT 1 FROM match_players mp JOIN matches m ON m.id = mp.match_id "
                           "WHERE mp.user_id = ? AND m.ranked = 1 LIMIT 1", (user_id,)) is not None

    def profile(self, login) -> Optional[Dict[str, object]]:
        """Publiczny profil: bilans, ranking, bogowie i ostatnie partie."""
        user = self._user(login)
        if user is None:
            return None
        totals = {"all": {"games": 0, "wins": 0}, "ranked": {"games": 0, "wins": 0}, "normal": {"games": 0, "wins": 0}}
        for row in self.db.query(
                "SELECT m.ranked, COUNT(*) AS games, SUM(mp.won) AS wins FROM match_players mp "
                "JOIN matches m ON m.id = mp.match_id WHERE mp.user_id = ? GROUP BY m.ranked", (user["id"],)):
            mode = "ranked" if row["ranked"] else "normal"
            totals[mode] = {"games": row["games"], "wins": row["wins"] or 0}
        totals["all"] = {key: totals["ranked"][key] + totals["normal"][key] for key in ("games", "wins")}
        for mode in totals.values():
            mode["losses"] = mode["games"] - mode["wins"]
        gods = [{"name": row["god"], "games": row["games"], "wins": row["wins"] or 0}
                for row in self.db.query(
                    "SELECT j.value AS god, COUNT(*) AS games, SUM(mp.won) AS wins "
                    "FROM match_players mp, json_each(mp.gods) j WHERE mp.user_id = ? "
                    "GROUP BY j.value ORDER BY games DESC, wins DESC, god", (user["id"],))]
        peak = self.db.one("SELECT MAX(rating_after) FROM match_players WHERE user_id = ?", (user["id"],))[0]
        return {"login": user["login"],
                "rating": user["rating"],
                "peak": max(peak or user["rating"], user["rating"]),
                "position": self.position(user["id"], user["rating"]),
                "since": user["created_at"],
                "totals": totals,
                "gods": gods,
                "history": self.history(user["id"])}

    def history(self, user_id: int, before: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, object]:
        """Ostatnie partie gracza, od najnowszej; `before` to id partii, od której ładować dalej."""
        limit = limit or self.HISTORY_PAGE
        rows = self.db.query(
            "SELECT m.id, m.ranked, m.rounds, m.forfeit, m.finished_at, me.won, me.hp, me.gods, "
            "me.rating_before, me.rating_after, op.name AS opponent, op.user_id IS NOT NULL AS opponent_account, "
            "op.hp AS opponent_hp, op.gods AS opponent_gods "
            "FROM match_players me JOIN matches m ON m.id = me.match_id "
            "JOIN match_players op ON op.match_id = me.match_id AND op.seat != me.seat "
            "WHERE me.user_id = ? AND (? IS NULL OR m.id < ?) ORDER BY m.id DESC LIMIT ?",
            (user_id, before, before, limit + 1))
        matches = [{"id": row["id"],
                    "ranked": bool(row["ranked"]),
                    "rounds": row["rounds"],
                    "forfeit": bool(row["forfeit"]),
                    "at": row["finished_at"],
                    "won": bool(row["won"]),
                    "hp": row["hp"],
                    "gods": json.loads(row["gods"]),
                    "rating": (None if row["rating_after"] is None
                               else {"before": row["rating_before"], "after": row["rating_after"]}),
                    "opponent": {"name": row["opponent"], "account": bool(row["opponent_account"]),
                                 "hp": row["opponent_hp"], "gods": json.loads(row["opponent_gods"])}}
                   for row in rows[:limit]]
        return {"matches": matches, "more": len(rows) > limit}

    def history_of(self, login, before=None) -> Optional[Dict[str, object]]:
        user = self._user(login)
        if user is None:
            return None
        before = before if isinstance(before, int) and not isinstance(before, bool) else None
        return dict(self.history(user["id"], before), login=user["login"])

    def ranking(self, limit: Optional[int] = None) -> List[Dict[str, object]]:
        """Najlepsi gracze rankingowi."""
        rows = self.db.query(
            "SELECT u.login, u.rating, COUNT(*) AS games, SUM(mp.won) AS wins "
            "FROM users u JOIN match_players mp ON mp.user_id = u.id "
            "JOIN matches m ON m.id = mp.match_id AND m.ranked = 1 "
            "GROUP BY u.id ORDER BY u.rating DESC, games DESC, u.login_key LIMIT ?",
            (limit or self.RANKING_SIZE,))
        players = []
        for i, row in enumerate(rows):
            # równy ranking, to samo miejsce (tak samo liczy position())
            tied = players and players[-1]["rating"] == row["rating"]
            players.append({"position": players[-1]["position"] if tied else i + 1,
                            "login": row["login"], "rating": row["rating"], "games": row["games"],
                            "wins": row["wins"] or 0, "losses": row["games"] - (row["wins"] or 0)})
        return players
