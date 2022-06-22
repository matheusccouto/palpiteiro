""" Palpiteiro web-app. """

import json

import pandas as pd
import requests
import streamlit as st


POS_MAP = {
    "goalkeeper": "GOL",
    "fullback": "LAT",
    "defender": "ZAG",
    "midfielder": "MEI",
    "forward": "ATA",
    "coach": "TEC",
}
POS_ORDER = {"GOL": 1, "LAT": 2, "ZAG": 3, "MEI": 4, "ATA": 5, "TEC": 6}

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


def format_html_table(html):
    """Format a html table."""
    html = html.replace("<table", "<table width=100%")
    html = html.replace(
        "<table",
        '<table style="text-align: left; border-collapse: collapse"',
    )
    html = html.replace("<td", '<td style="border: none"')
    html = html.replace("<tr", '<tr style="border: none"', 1)
    return html


def create_html_tag(photo, height, name=None):
    """Create html tag with image."""
    if name:
        name = f" {name}"
    else:
        name = ""
    return f'<img src="{photo}" height="{height}">{name}'


def json2html(data):
    """Convert JSON to a formatted HTML"""
    data = pd.DataFrame(data)
    data["__player__"] = data.apply(
        lambda x: create_html_tag(photo=x["photo"], name=x["name"], height=32),
        axis=1,
    ).str.pad(256)

    data["__club__"] = data.apply(
        lambda x: create_html_tag(photo=x["club_badge"], height=32),
        axis=1,
    ).str.pad(256)

    data["__position__"] = data["position"].replace(POS_MAP)
    data["__order__"] = data["__position__"].replace(POS_ORDER)
    data = data.sort_values("__order__", ascending=True)

    data = data[["__position__", "__club__", "__player__"]]
    html_table = data.to_html(escape=False, header=False, index=False, border=0)
    return format_html_table(html_table)


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
    )

    if res.status_code >= 300:
        st.error(ERROR_MSG)
        st.stop()

    data = res.json()
    if data["status"] != "SUCCEEDED":
        st.error(ERROR_MSG)
        st.stop()

    output = json.loads(data["output"])
    return output["players"], output["bench"]


def main():
    """Main routine"""
    # Page title and configs.
    st.set_page_config(page_title="Palpiteiro", page_icon=":soccer:")
    st.title("Palpiteiro")
    st.text("Recomendação de escalações para o Cartola FC")

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
        players, bench = get_line_up(budget, SCHEME, MAX_PLAYERS_PER_CLUB)
        st.write(json2html(players.copy()), unsafe_allow_html=True)
        st.header("")
        st.write(json2html(bench.copy()), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
