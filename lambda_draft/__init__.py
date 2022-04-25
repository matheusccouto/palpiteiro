"""Azure function."""

import json
from typing import Any, Callable, Dict, List

from .draft import Player, Scheme
from .draft.algorithm.genetic import Genetic


def parse_scheme(scheme: Dict[str, int]) -> Scheme:
    """Parse scheme argument."""
    return Scheme(**scheme)


def parse_algorithm(name: str) -> Callable:
    """Parse algorithm argument."""
    if "genetic" in name.lower():
        return Genetic
    raise ValueError(f"{name} is not a valid algorithm")


def parse_players(players: List[Dict[str, Any]]) -> List[Player]:
    """Parse players argument."""
    return [Player(**player) for player in players]


def parse_price(price: float) -> float:
    """Parse price argument."""
    if price <= 0:
        raise ValueError("Price should be positive")
    return price


def parse_max_players_per_club(max_players_per_club: float) -> float:
    """Parse min_clubs argument."""
    max_players_per_club = int(max_players_per_club)
    if max_players_per_club < 1:
        raise ValueError("Max players per club should be greater than zero.")
    return max_players_per_club


def handler(event, context):  # pylint: disable=unused-argument
    """Lambda handler."""
    scheme = parse_scheme(event["scheme"])
    algo_class = parse_algorithm(event["algorithm"])
    players = parse_players(event["players"])
    price = parse_price(event["price"])
    max_players_per_club = parse_max_players_per_club(event["max_players_per_club"])

    line_up = algo_class(players).draft(price, scheme, max_players_per_club)

    body = dict(players=line_up.players, bench=line_up.bench)
    return json.loads(json.dumps(body, default=vars))
