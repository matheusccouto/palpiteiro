"""Dropout players."""

import random


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    players = event["players"]
    dropout = event["dropout"]
    random.shuffle(players)
    return players[: int(len(players) * (1 - dropout))]
