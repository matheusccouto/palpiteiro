"""Extract players data from Cartola FC."""

import os

import utils.aws

PLAYERS_URL = "https://api.cartola.globo.com/atletas/mercado"
STATUS_URL = "https://api.cartola.globo.com/mercado/status"
BUCKET = os.environ["BUCKET"]


def handler(event, context=None):
    """Lambda handler."""
    status = utils.aws.get(STATUS_URL)
    if status["game_over"]:
        raise ConnectionAbortedError("Extraction aborted. Game is over.")

    players = utils.aws.get(PLAYERS_URL)

    # This endpoint returns has no reference at all for which season this is.
    # This is important to us as we work with multiseason data.
    # I'll include it inside the players that that are inside the 'atletas' key.

    season = status["temporada"]
    rnd = players["atletas"][0]["rodada_id"]

    for player in players["atletas"]:
        player["temporada_id"] = season

    uri = utils.aws.to_s3(
        data=players,
        bucket=BUCKET,
        key=f"atletas/mercado/{season}-{rnd}.json",
    )
    return {"uri": uri}
