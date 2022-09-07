{% macro predict_points() %}

CREATE OR REPLACE FUNCTION {{ target.dataset }}.predict_points(
    position STRING,
    total_points_last_5_at,
    offensive_points_last_5_at,
    defensive_points_last_5_at,
    spi_club,
    spi_opponent,
    prob_club,
    prob_opponent,
    prob_tie,
    importance_club,
    importance_opponent,
    proj_score_club,
    proj_score_opponent,
    total_points_club_last_5_at,
    offensive_points_club_last_5_at,
    defensive_points_club_last_5_at,
    total_allowed_points_opponent_last_5_at,
    offensive_allowed_points_opponent_last_5_at,
    defensive_allowed_points_opponent_last_5_at,
    played_last_5 INT64,
    avg_odds_club,
    avg_odds_opponent,
    avg_odds_draw
) RETURNS REMOTE WITH CONNECTION `us-east4.remote-function` OPTIONS (
    endpoint = 'https://us-east4-palpiteiro-{{ target.name }}.cloudfunctions.net/points',
    user_defined_context = {
        "names": [
            "position",
            "total_points_last_5_at",
            "offensive_points_last_5_at",
            "defensive_points_last_5_at",
            "spi_club",
            "spi_opponent",
            "prob_club",
            "prob_opponent",
            "prob_tie",
            "importance_club",
            "importance_opponent",
            "proj_score_club",
            "proj_score_opponent",
            "total_points_club_last_5_at",
            "offensive_points_club_last_5_at",
            "defensive_points_club_last_5_at",
            "total_allowed_points_opponent_last_5_at",
            "offensive_allowed_points_opponent_last_5_at",
            "defensive_allowed_points_opponent_last_5_at",
            "played_last_5",
            "avg_odds_club",
            "avg_odds_opponent",
            "avg_odds_draw"
            ]
        }
    )

{% endmacro %}