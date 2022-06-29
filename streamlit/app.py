""" Palpiteiro web-app. """

import json
import os
import concurrent.futures
from PIL import Image

import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st

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
SPINNER_MSG = ""


@st.cache(
    show_spinner=False,
    hash_funcs={"_json.Scanner": hash},
    allow_output_mutation=True,
)
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
    data = data.copy()
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
        source=Image.open(photo),
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
        source=Image.open(logo),
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


def download_image(url, session):
    """Download image."""
    return session.get(url, stream=True).raw


def transform_row(row):
    """Transform rows values."""
    session = requests.session()
    row["photo"] = download_image(row["photo"], session)
    row["club_badge"] = download_image(row["club_badge"], session)
    return row


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

        with concurrent.futures.ThreadPoolExecutor(5) as executor:
            futures = [
                executor.submit(transform_row, row) for _, row in data.iterrows()
            ]
            for future in concurrent.futures.as_completed(futures):
                row = future.result()
                add_player_image(
                    fig=fig,
                    x=row["x"],
                    y=row["y"],
                    name=row["name"],
                    photo=row["photo"],
                    logo=row["club_badge"],
                    price=row["price"],
                )

        fig.update_layout(
            height=450,
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


if __name__ == "__main__":
    main()
