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
    avg_odds_club,
    avg_odds_opponent,
    avg_odds_draw,
    total_points
FROM
    palpiteiro.fct_player
WHERE
    status = 'expected'
    AND played IS TRUE
    AND played_last_5 > 0
    AND valid_club_last_5 > 0
    AND position != 'coach'
    AND all_time_round >= (SELECT MAX(all_time_round) FROM cartola.fct_match) - 38