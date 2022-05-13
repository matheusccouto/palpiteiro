"""Lambda function."""

import json

from .draft import Player, Scheme
from .draft.algorithm.genetic import Genetic


def handler(event, context):  # pylint: disable=unused-argument
    """Lambda handler."""
    scheme = Scheme(**event["scheme"])
    players = [Player(**player) for player in event["players"]]
    price = float(event["price"])
    max_players_per_club = int(event["max_players_per_club"])

    line_up = Genetic(players).draft(price, scheme, max_players_per_club)

    body = dict(players=line_up.players, bench=line_up.bench)
    return json.loads(json.dumps(body, default=vars))
