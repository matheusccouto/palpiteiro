""" Palpiteiro web-app. """

import json
import os

import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

THIS_DIR = os.path.dirname(__file__)


POS = [
    "goalkeeper",
    "fullback",
    "defender",
    "midfielder",
    "forward",
    "coach",
]

# Default values
SCHEME = {
    "goalkeeper": 1,
    "fullback": 2,
    "defender": 2,
    "midfielder": 3,
    "forward": 3,
    "coach": 1,
}
MAX_PLAYERS_PER_CLUB = 5

# Messages
ERROR_MSG = "Foi mal, tivemos um erro"
SPINNER_MSG = "Por favor aguarde enquanto o algoritmo escolhe os jogadores"


def make_plot(data):

    # Y position per position
    Y = {"coach": 0.125, "goalkeeper": 0.125, "defender": 0.367, "midfielder": 0.633, "forward": 0.875}

    fig = go.Figure()

    # Background
    fig.add_layout_image(
        dict(
            source=Image.open(os.path.join(THIS_DIR, "pitch.png")),
            xref="paper",
            yref="paper",
            x=0,
            y=0,
            sizex=1,
            sizey=1,
            xanchor="left",
            yanchor="bottom",
            layer="below",
            sizing="stretch",
        )
    )

    # Separe player per position.
    pos_players = {
        pos: [p for p in data["players"] if p["position"] == pos] for pos in POS
    }

    # Insert defender in the middle of the fullbacks and remove fullbacks key
    cut = int(len(pos_players["fullback"]) / 2)
    pos_players["defender"] = (
        pos_players["fullback"][:cut]
        + pos_players["defender"]
        + pos_players["fullback"][cut:]
    )
    pos_players.pop("fullback")

    for pos, players in pos_players.items():
        for i, player in enumerate(players):

            x = (i + 0.5) / len(players)
            y = Y[pos]

            if player["position"] == "fullback":
                y += 0.025

            if player["position"] == "defender":
                y -= 0.025
            
            if player["position"] == "coach":
                x = 0.125

            fig.add_layout_image(
                dict(
                    source=Image.open(
                        requests.get(player["photo"], stream=True, verify=False).raw
                    ),
                    xref="paper",
                    yref="paper",
                    x=x,
                    y=y,
                    sizex=0.2,
                    sizey=0.2,
                    xanchor="center",
                    yanchor="middle",
                )
            )
            fig.add_annotation(
                xref="paper",
                yref="paper",
                x=x,
                y=y - 0.09,
                xanchor="center",
                yanchor="middle",
                text=player["name"],
                showarrow=False,
                font=dict(color="white", size=24, family='monospace'),
            )
    
    # for iplayer in enumerate(data["bench"]):

    fig.update_layout(
        autosize=False,
        height=900,
        width=600,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=100),
    )
    return fig


# @st.cache(show_spinner=False)
def get_line_up(budget, scheme, max_players_per_club):
    """Request a line up."""
    res = requests.post(
        url=st.secrets["API_URL"],
        headers={
            "x-api-key": st.secrets["API_KEY"],
            "Content-Type": "application/json",
        },
        json={
            "scheme": scheme,
            "price": budget,
            "max_players_per_club": max_players_per_club,
        },
        verify=False,
    )

    if res.status_code >= 300:
        st.error(ERROR_MSG)
        st.stop()

    data = res.json()
    if data["status"] != "SUCCEEDED":
        st.error(ERROR_MSG)
        st.stop()

    return json.loads(data["output"])


def main():
    """Main routine"""
    # Page title and configs.
    st.set_page_config(page_title="Palpiteiro", page_icon=":soccer:")
    st.title(":soccer: Palpiteiro")
    # Inputs
    budget = st.sidebar.number_input(
        "Cartoletas",
        min_value=0.0,
        value=100.0,
        step=0.1,
        format="%.1f",
    )

    # Main body
    with st.spinner(SPINNER_MSG):
        data = get_line_up(budget, SCHEME, MAX_PLAYERS_PER_CLUB)
        st.plotly_chart(make_plot(data), config={'displayModeBar': False})


if __name__ == "__main__":
    main()
