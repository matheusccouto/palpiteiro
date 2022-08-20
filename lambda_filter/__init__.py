"""Filter players by their matches date."""

from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    players = event["players"]
    date = event.get("date")
    if date is not None:

        selected_timestamp = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=TZ)
        selected_date = selected_timestamp.date()
        event["players"] = [
            p
            for p in players
            if datetime.fromisoformat(p["timestamp"]).astimezone(TZ).date()
            == selected_date
        ]

    return event
