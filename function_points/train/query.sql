SELECT
    id, -- index
    all_time_round, -- time index
    club, -- draft only
    price_cartola_express AS price, -- draft only
    position,
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
    played_last_5,
    avg_odds_club,
    avg_odds_opponent,
    avg_odds_draw,
    total_points -- target
FROM
    palpiteiro.fct_player
WHERE
    status = 'expected'
    AND played IS TRUE
    AND played_last_5_at > 0
    AND valid_club_last_5_at > 0
    AND valid_opponent_last_5_at > 0