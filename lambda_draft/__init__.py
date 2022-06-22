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

    body = dict(players=line_up.players, bench=line_up.bench)
    return json.loads(json.dumps(body, default=vars))
