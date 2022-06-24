SELECT
    s.player,
    s.all_time_round,
    c.club,
    c.valid,
    s.position,
    s.status,
    s.price,
    s.played,
    s.total_points,
    s.offensive_points,
    s.defensive_points,
    c.spi_club,
    c.spi_opponent,
    c.prob_club,
    -- Add 0.1 to avoid division by zero)
    c.prob_opponent,
    -- Add 0.1 to avoid division by zero)
    c.prob_tie,
    -- Add 0.1 to avoid division by zero)
    c.importance_club,
    -- Add 0.1 to avoid division by zero)
    c.importance_opponent,
    -- Add 0.1 to avoid division by zero)
    c.proj_score_club,
    -- Add 0.1 to avoid division by zero)
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
    AVG(
        s.total_points
    ) OVER (
        PARTITION BY
            s.player, c.home
        ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
    ) AS total_points_last_5,
    AVG(
        s.offensive_points
    ) OVER (
        PARTITION BY
            s.player, c.home
        ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
    ) AS offensive_points_last_5,
    AVG(
        s.defensive_points
    ) OVER (
        PARTITION BY
            s.player, c.home
        ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
    ) AS defensive_points_last_5,
    s.total_points / (c.total_points_club + 0.1) AS total_points_repr,
    s.offensive_points / (
        c.offensive_points_club + 0.1
    ) AS offensive_points_repr,
    s.defensive_points / (
        c.defensive_points_club + 0.1
    ) AS defensive_points_repr,
    AVG(
        s.total_points / (c.total_points_club + 0.1)
    ) OVER (
        PARTITION BY
            s.player, c.home
        ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
    ) AS total_points_repr_last_5,
    AVG(
        s.offensive_points / (c.offensive_points_club + 0.1)
    ) OVER (
        PARTITION BY
            s.player, c.home
        ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
    ) AS offensive_points_repr_last_5,
    AVG(
        s.defensive_points / (c.defensive_points_club + 0.1)
    ) OVER (
        PARTITION BY
            s.player, c.home
        ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
    ) AS defensive_points_repr_last_5
FROM
    {{ ref ("fct_scoring") }} AS s
INNER JOIN
    {{ ref ("fct_club") }} AS c ON
        s.club = c.club AND s.all_time_round = c.all_time_round
