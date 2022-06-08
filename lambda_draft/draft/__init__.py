"""Cartola FC line-up draft."""

from dataclasses import dataclass
from typing import Dict, Generator, Iterator, List


@dataclass
class Player:
    """Player"""

    id: int  # pylint: disable=invalid-name
    position: str
    price: float
    points: float
    club: int

    def __eq__(self, other):
        return self.id == other.id


@dataclass
class Scheme:
    """Line-up scheme."""

    goalkeeper: int
    defender: int
    fullback: int
    midfielder: int
    forward: int
    coach: int

    def to_dict(self):
        """Convert scheme instance to a dict instance."""
        return {
            "goalkeeper": self.goalkeeper,
            "defender": self.defender,
            "fullback": self.fullback,
            "midfielder": self.midfielder,
            "forward": self.forward,
            "coach": self.coach,
        }

    def items(self) -> Iterator:
        """Iterate of items."""
        return self.to_dict().items()

    def keys(self) -> Iterator:
        """Iterate of keys."""
        return self.to_dict().keys()


@dataclass
class LineUp:
    """Squad line-up"""

    scheme: Scheme
    players: List[Player]
    bench: List[Player]

    def __post_init__(self):
        self.players = sorted(self.players, key=lambda x: x.position)
        self.bench = sorted(self.bench, key=lambda x: x.position)

    def __iter__(self) -> Generator:
        for player in self.players:
            yield player

    @property
    def points(self):
        """Get line-up points."""
        return sum(player.points for player in self.players)

    @property
    def price(self):
        """Get line-up price."""
        return sum(player.price for player in self.players)

    @property
    def players_per_position(self) -> Dict[str, List[Player]]:
        """Get line-up players by position."""
        return {
            pos: [player for player in self.players if player.position == pos]
            for pos in self.scheme.keys()
        }

    @property
    def missing(self) -> Dict[str, int]:
        """Check if line-up still missing players from a certain position."""
        return {
            key: val - len(self.players_per_position[key])
            for key, val in self.scheme.items()
        }

    @property
    def players_per_club(self):
        """Get players per club."""
        count = {}
        for player in self.players:
            if player.club not in count:
                count[player.club] = 1
            else:
                count[player.club] += 1
        return count

    @property
    def max_players_per_club(self):
        """Get max players per club."""
        return max(self.players_per_club.values())

    def add_player(self, player: Player):
        """Add player to the line-up."""
        self.players.append(player)

    def remove_player(self, player: Player):
        """Remove player from the line-up."""
        self.players.remove(player)

    def is_valid(self) -> bool:
        """Check if line up is valid."""
        return all(count == 0 for count in self.missing.values())

    def copy(self) -> "LineUp":
        """Copy this instance."""
        return LineUp(scheme=self.scheme, players=self.players, bench=self.bench)
