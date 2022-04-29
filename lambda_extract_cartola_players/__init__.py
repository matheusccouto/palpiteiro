"""Extract players data from Cartola FC"""

import json

import urllib3

PLAYERS_URL = "https://api.cartola.globo.com/atletas/mercado"
STATUS_URL = "https://api.cartola.globo.com/mercado/status"


def get(url):
    """Make a GET request without specifying any body or header."""
    return json.loads(urllib3.PoolManager().request("GET", url).data.decode("utf-8"))


def handler(event, context):
    """Lambda handler."""
    status = get(STATUS_URL)
    if status["game_over"]:
        raise ConnectionAbortedError("Extraction aborted. Game is over.")

    players = get(PLAYERS_URL)

    # This endpoint returns has no reference at all for which season this is.
    # This is important to us as we work with multiseason data.
    # I'll include it inside the players that that are inside the 'atletas' key.

    for player in players["atletas"]:
        player["temporada_id"] = status["temporada"]

    return players