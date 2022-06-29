""" Palpiteiro web-app. """

import base64
import json
import os
from PIL import Image

import altair as alt
import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st

# Config
alt.renderers.set_embed_options(actions=False)

# Dirs
THIS_DIR = os.path.dirname(__file__)

# Vars
API_URL = st.secrets["API_URL"]
API_KEY = st.secrets["API_KEY"]

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


def get_image(url):
    """Get image from URL"""
    return f"data:image/png;base64,{base64.b64encode(requests.get(url, stream=True).raw.read()).decode()}"


def make_plot_(data):
    """Create plot."""


def make_plot_(data):
    """Create plot."""

    # Y position per position
    Y = {
        "coach": 0.125,
        "goalkeeper": 0.125,
        "defender": 0.367,
        "midfielder": 0.633,
        "forward": 0.875,
    }

    # fig = go.Figure()

    # # Background
    # fig.add_layout_image(
    #     dict(
    #         source=Image.open(os.path.join(THIS_DIR, "pitch.png")),
    #         xref="paper",
    #         yref="paper",
    #         x=0,
    #         y=0,
    #         sizex=1,
    #         sizey=1,
    #         xanchor="left",
    #         yanchor="bottom",
    #         layer="below",
    #         sizing="stretch",
    #     )
    # )

    # Separe player per position.
    pos_players = {
        pos: [p for p in data["players"] if p["position"] == pos]
        for pos in SCHEME.keys()
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

            #         img = Image.open(requests.get(player["photo"], stream=True).raw)

            #         fig.add_layout_image(
            #             dict(
            #                 source=img,
            #                 xref="x",
            #                 yref="y",
            #                 x=x,
            #                 y=y,
            #                 sizex=0.2,
            #                 sizey=0.2,
            #                 xanchor="center",
            #                 yanchor="middle",
            #             )
            #         )

            #         img_club = Image.open(requests.get(player["club_badge"], stream=True).raw)

            fig.add_layout_image(
                dict(
                    source=img_club,
                    xref="x",
                    yref="y",
                    x=x + 0.02,
                    y=y - 0.02,
                    sizex=0.1,
                    sizey=0.1,
                    xanchor="left",
                    yanchor="top",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=[x],
                    y=[y],
                    mode="markers+text",
                    marker=dict(size=65, color="rgba(0,0,0,0)"),
                    text=player["name"],
                    textposition="bottom center",
                    hovertemplate=f"${player['price']}<extra></extra>",
                    hoverlabel=dict(bgcolor="white", font_family="monospace"),
                    textfont=dict(family="monospace"),
                ),
            )

    # fig.update_layout(
    #     height=600,
    #     width=350,
    #     plot_bgcolor="rgba(0,0,0,0)",
    #     xaxis=dict(visible=False, fixedrange=True),
    #     yaxis=dict(visible=False, fixedrange=True),
    #     margin=dict(l=0, r=0, t=0, b=100),
    #     showlegend=False,
    # )
    # return fig


def get_line_up(budget, scheme, max_players_per_club, url, key):
    """Request a line up."""
    res = requests.post(
        url=url,
        headers={
            "x-api-key": key,
            "Content-Type": "application/json",
        },
        json={
            "scheme": scheme,
            "price": budget,
            "max_players_per_club": max_players_per_club,
        },
    )

    if res.status_code >= 300:
        st.error(ERROR_MSG)
        st.stop()

    data = res.json()
    if data["status"] != "SUCCEEDED":
        st.error(ERROR_MSG)
        st.stop()

    output = json.loads(data["output"])
    players = pd.DataFrame.from_records(output["players"])
    bench = pd.DataFrame.from_records(output["bench"])

    # Identify the rows before joining.
    players["type"] = "players"
    bench["type"] = "bench"

    return pd.concat([players, bench])


def transform_data(data):
    """Transform data for plotting."""
    data["club_badge"] = data["club_badge"].apply(get_image)
    data["photo"] = data["photo"].apply(get_image)

    data["rank"] = data.groupby(["position", "type"])["id"].rank().astype(int)
    data["plot"] = data.apply(
        lambda x: f'{x["type"]}-{x["position"]}-{x["rank"]}', axis=1
    )

    with open(os.path.join(THIS_DIR, "pos.json"), encoding="utf-8") as f:
        pos = json.load(f)

    data["x"] = data["plot"].apply(lambda x: pos[x]["x"])
    data["y"] = data["plot"].apply(lambda x: pos[x]["y"])
    data["badge_x"] = data["x"] + 0.025
    data["badge_y"] = data["y"] - 0.075

    return data


def add_player_image(fig, x, y, name, photo, logo, price):
    """Add player image."""
    fig.add_layout_image(
        source=photo,
        xref="x",
        yref="y",
        x=x,
        y=y,
        sizex=0.15,
        sizey=0.15,
        xanchor="center",
        yanchor="middle",
    )
    fig.add_layout_image(
        source=logo,
        xref="x",
        yref="y",
        x=x + 0.01,
        y=y - 0.015,
        sizex=0.075,
        sizey=0.075,
        xanchor="left",
        yanchor="top",
    )

    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            marker=dict(size=50, color="rgba(0,0,0,0)"),
            text=name,
            textposition="bottom center",
            hovertemplate=f"${price}<extra></extra>",
        ),
    )


def main():
    """Main routine"""
    # Page title and configs.
    st.set_page_config(page_title="Palpiteiro", page_icon=":soccer:")
    st.title("Palpiteiro")

    # Inputs
    budget = st.sidebar.number_input(
        "Budget",
        min_value=0.0,
        value=100.0,
        step=0.1,
        format="%.1f",
    )

    with st.spinner(SPINNER_MSG):

        data = get_line_up(
            budget=budget,
            scheme=SCHEME,
            max_players_per_club=MAX_PLAYERS_PER_CLUB,
            url=API_URL,
            key=API_KEY,
        )
        data = transform_data(data)

        fig = go.Figure()
        fig.add_layout_image(
            source=Image.open(os.path.join(THIS_DIR, "pitch.png")),
            xref="paper",
            yref="y",
            x=0,
            y=0,
            sizex=1,
            sizey=1,
            xanchor="left",
            yanchor="bottom",
            layer="below",
            sizing="stretch",
        )
        for i, row in data.iterrows():
            add_player_image(
                fig,
                x=row["x"],
                y=row["y"],
                name=row["name"],
                photo=row["photo"],
                logo=row["club_badge"],
                price=row["price"],
            )
        fig.update_layout(
            height=500,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, fixedrange=True),
            yaxis=dict(visible=False, fixedrange=True),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )
        st.plotly_chart(
            fig,
            config={"displayModeBar": False},
            use_container_width=True,
        )

        # c = alt.Chart(data)
        # c = c.mark_image(width=65, height=65).encode(
        #     x=alt.X("x", axis=None),
        #     y=alt.Y("y", axis=None),
        #     url="photo",
        #     text="name",
        #     tooltip="price",
        # )
        # c = c + c.mark_image(width=30, height=30).encode(
        #     # dx=10,
        #     # dy=10,
        #     url="club_badge",
        #     text="name",
        # )
        # text = c + c.mark_text(
        #     align="center",
        #     baseline="middle",
        #     dy=45,  # Nudges text to right so it doesn't appear on top of the bar
        #     color="white"
        # ).encode(text="name")
        # c = c.configure_view(strokeOpacity=0, strokeWidth=0).properties(height=500)
        # st.altair_chart(c, use_container_width=True)


if __name__ == "__main__":
    main()
