{% macro points() %}

CREATE OR REPLACE FUNCTION palpiteiro.points(
    position STRING,
    total_points_last_5 FLOAT64,
    offensive_points_last_5 FLOAT64,
    defensive_points_last_5 FLOAT64,
    total_points_repr_last_5 FLOAT64,
    offensive_points_repr_last_5 FLOAT64,
    defensive_points_repr_last_5 FLOAT64,
    spi_club FLOAT64,
    spi_opponent FLOAT64,
    prob_club FLOAT64,
    prob_opponent FLOAT64,
    prob_tie FLOAT64,
    importance_club FLOAT64,
    importance_opponent FLOAT64,
    proj_score_club FLOAT64,
    proj_score_opponent FLOAT64,
    total_points_club_last_5 FLOAT64,
    offensive_points_club_last_5 FLOAT64,
    defensive_points_club_last_5 FLOAT64,
    total_allowed_points_opponent_last_5 FLOAT64,
    offensive_allowed_points_opponent_last_5 FLOAT64,
    defensive_allowed_points_opponent_last_5 FLOAT64
) RETURNS FLOAT64 REMOTE WITH CONNECTION `us-east4.remote-function` OPTIONS (
    endpoint = 'https://us-east4-palpiteiro-{{ target.name }}.cloudfunctions.net/points'
)

{% endmacro %}