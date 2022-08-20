"""Unit tests for the lambda function."""

import json
import os

import pytest

import lambda_cartola_bot

THIS_DIR = os.path.dirname(__file__)


@pytest.fixture(name="event")
def event_fixture():
    """Mock typical event."""
    with open(os.path.join(THIS_DIR, "sample.json"), encoding="utf-8") as file:
        yield json.load(file)


def test_bot(event):
    """Test if JSON file exists."""
    res = lambda_cartola_bot.handler(event=event, context=None)
    assert res["mensagem"] != "Usuário não autorizado"
    assert res["mensagem"] != "Houve algum problema e seu time não foi escalado. Tente novamente!"
