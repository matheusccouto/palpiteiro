SELECT
    s.player,
    s.name,
    s.round,
    s.season,
    s.all_time_round,
    c.club,
    c.opponent,
    c.home,
    s.position,
    s.status,
    s.price,
    s.variation,
    s.played,
    s.total_points,
    s.offensive_points,
    s.defensive_points,
    s.total_points / (c.total_points_club + 0.1) AS total_points_repr, -- Add 0.1 to avoid division by zero)
    s.offensive_points / (c.offensive_points_club + 0.1) AS offensive_points_repr, -- Add 0.1 to avoid division by zero)
    s.defensive_points / (c.defensive_points_club + 0.1) AS defensive_points_repr, -- Add 0.1 to avoid division by zero)
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
    c.defensive_allowed_points_opponent_last_5
FROM
    {{ ref ("fct_scoring") }} s
    LEFT JOIN {{ ref ("fct_club") }} c ON s.club = c.club AND s.all_time_round = c.all_time_round