"""Unit tests for the lambda function."""

import pytest

import lambda_cartola_bot


@pytest.fixture(name="event")
def event_fixture():
    """Mock typical event."""
    yield {
        "players": [
            {"id": 42234, "points": 12},
            {"id": 97899, "points": 9.5},
            {"id": 104649, "points": 10.4},
            {"id": 38632, "points": 16.5},
            {"id": 99881, "points": 18.5},
            {"id": 69705, "points": 10},
            {"id": 70986, "points": 13.3},
            {"id": 81091, "points": 9.8},
            {"id": 38162, "points": 12},
            {"id": 62033, "points": 17.4},
            {"id": 86485, "points": 11.4},
        ],
        "bench": [
            {"id": 69012, "points": 9, "position": "goalkeeper"},
            {"id": 100846, "points": 1.6, "position": "fullback"},
            {"id": 84263, "points": 8.1, "position": "defender"},
            {"id": 104526, "points": 8.3, "position": "midfielder"},
            {"id": 107745, "points": 5.8, "position": "forward"},
        ],
    }


def test_bot(event):
    """Test if JSON file exists."""
    res = lambda_cartola_bot.handler(event=event, context=None)
    assert res["mensagem"] != "Usuário não autorizado"	
