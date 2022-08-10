SELECT
    id,
    position,
    total_points_last_5,
    offensive_points_last_5,
    defensive_points_last_5,
    total_points_repr_last_5,
    offensive_points_repr_last_5,
    defensive_points_repr_last_5,
    spi_club,
    spi_opponent,
    prob_club,
    prob_opponent,
    prob_tie,
    importance_club,
    importance_opponent,
    proj_score_club,
    proj_score_opponent,
    total_points_club_last_5,
    offensive_points_club_last_5,
    defensive_points_club_last_5,
    total_allowed_points_opponent_last_5,
    offensive_allowed_points_opponent_last_5,
    defensive_allowed_points_opponent_last_5,
    penalties_club_last_5,
    penalties_opponent_last_5,
    received_penalties_club_last_5,
    received_penalties_opponent_last_5,
    played_last_5,
    IF(total_points <= 0.01, 0.01, total_points) AS total_points
FROM
    palpiteiro.fct_player
WHERE
    played IS TRUE
    AND position != 'coach'
    AND all_time_round >= (SELECT MAX(all_time_round) FROM cartola.fct_match) - 38