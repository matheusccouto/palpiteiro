SELECT
    s.id,
    s.player,
    s.all_time_round,
    c.timestamp,
    c.club,
    c.valid,
    s.position,
    s.status,
    s.price AS price_cartola,
    s.price - s.variation AS price_cartola_express,
    s.played,
    s.total_points,
    s.offensive_points,
    s.defensive_points,
    c.spi_club,
    c.spi_opponent,
    c.prob_club,
    c.prob_opponent,
    c.prob_tie,
    c.importance_club,
    c.importance_opponent,
    c.proj_score_club,
    c.proj_score_opponent,
    c.total_points_club,
    c.offensive_points_club,
    c.defensive_points_club,
    c.total_points_opponent,
    c.offensive_points_opponent,
    c.defensive_points_opponent,
    c.total_points_club_last_5,
    c.offensive_points_club_last_5,
    c.defensive_points_club_last_5,
    c.total_allowed_points_opponent_last_5,
    c.offensive_allowed_points_opponent_last_5,
    c.defensive_allowed_points_opponent_last_5,
    AVG(s.total_points) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS total_points_last_5,
    AVG(s.offensive_points) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS offensive_points_last_5,
    AVG(s.defensive_points) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS defensive_points_last_5,
    s.total_points / (c.total_points_club + 0.1) AS total_points_repr,
    s.offensive_points / (c.offensive_points_club + 0.1) AS offensive_points_repr, -- Add 0.1 to avoid division by zero)
    s.defensive_points / (c.defensive_points_club + 0.1 ) AS defensive_points_repr, -- Add 0.1 to avoid division by zero)
    AVG(s.total_points / (c.total_points_club + 0.1)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS total_points_repr_last_5, -- Add 0.1 to avoid division by zero)
    AVG(s.offensive_points / (c.offensive_points_club + 0.1)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS offensive_points_repr_last_5, -- Add 0.1 to avoid division by zero)
    AVG(s.defensive_points / (c.defensive_points_club + 0.1)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS defensive_points_repr_last_5, -- Add 0.1 to avoid division by zero)
    c.penalties_club_last_5,
    c.penalties_opponent_last_5,
    c.received_penalties_club_last_5,
    c.received_penalties_opponent_last_5,
    COALESCE(SUM(CAST(s.played AS INT64)) OVER (PARTITION BY s.player ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS played_last_5,
    COALESCE(SUM(CAST(s.played AS INT64)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS played_last_5_at,    c.pinnacle_odds_club,
    c.pinnacle_odds_opponent,
    c.pinnacle_odds_draw,
    c.max_odds_club,
    c.max_odds_opponent,
    c.max_odds_draw,
    c.avg_odds_club,
    c.avg_odds_opponent,
    c.avg_odds_draw
FROM
    {{ ref ("fct_scoring") }} AS s
INNER JOIN
    {{ ref ("fct_club") }} AS c ON
        s.club = c.club AND s.all_time_round = c.all_time_round
