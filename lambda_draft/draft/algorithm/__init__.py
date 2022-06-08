"""Cartola FC optimization algorithms."""

import abc
from typing import Dict, Sequence, List

from .. import Player, Scheme, LineUp

POSITIONS = ["goalkeeper", "fullback", "defender", "midfielder", "forward", "coach"]


def players_per_position(players: Sequence[Player]) -> Dict[str, List[Player]]:
    """Organize players by position."""
    return {
        pos: [player for player in players if player.position == pos]
        for pos in POSITIONS
    }


class DraftError(Exception):
    """Error on drafting players."""


class BaseAlgorithm(abc.ABC):
    """Algorithm base class."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def __init__(self, players: List[Player]):
        """Initializer"""
        self.players = players
        self.players_per_position = players_per_position(self.players)

    def _draft_bench(self, line_up: LineUp) -> List[Player]:
        """Draft players for the bench of a given line up."""
        bench = []
        for pos, count in line_up.scheme.items():

            if "coach" in pos:
                continue

            if count > 0:
                price = min(p.price for p in players_per_position(line_up.players)[pos])
                players = [
                    p
                    for p in self.players_per_position[pos]
                    if p.price <= price and p not in line_up.players
                ]
                if len(players) == 0:
                    continue
                player = sorted(players, key=lambda p: p.points)[-1]
                bench.append(player)

        return bench

    @abc.abstractmethod
    def draft(self, price: float, scheme: Scheme, max_players_per_club: int) -> LineUp:
        """Draft players following an specified scheme."""
