"""Lambda function."""

import json

from .draft import Player, Scheme
from .draft.algorithm.genetic import Genetic


def handler(event, context):  # pylint: disable=unused-argument
    """Lambda handler."""
    scheme = Scheme(**event["scheme"])
    price = float(event["price"])
    max_players_per_club = int(event["max_players_per_club"])
    players = [
        Player(
            id=player["id"],
            position=player["position"],
            price=player["price"],
            points=player["points"],
            club=player["club"],
        )
        for player in event["players"]
    ]

    line_up = Genetic(players).draft(price, scheme, max_players_per_club)

    players = [player.id for player in line_up.players]
    bench = [player.id for player in line_up.bench]
    return {
        "players": [p for p in event["players"] if p["id"] in players],
        "bench": [p for p in event["players"] if p["id"] in bench],
    }
