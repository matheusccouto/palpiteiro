WITH p AS (
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
        AVG(s.total_points) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_last_5,
        AVG(s.offensive_points) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_last_5,
        AVG(s.defensive_points) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_last_5,
        s.total_points / (c.total_points_club + 0.1) AS total_points_repr, -- Add 0.1 to avoid division by zero)
        s.offensive_points / (c.offensive_points_club + 0.1) AS offensive_points_repr, -- Add 0.1 to avoid division by zero)
        s.defensive_points / (c.defensive_points_club + 0.1) AS defensive_points_repr, -- Add 0.1 to avoid division by zero)
        AVG(s.total_points / (c.total_points_club + 0.1)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_repr_last_5, -- Add 0.1 to avoid division by zero)
        AVG(s.offensive_points / (c.offensive_points_club + 0.1)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_repr_last_5, -- Add 0.1 to avoid division by zero)
        AVG(s.defensive_points / (c.defensive_points_club + 0.1)) OVER (PARTITION BY s.player, c.home ORDER BY s.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_repr_last_5, -- Add 0.1 to avoid division by zero)
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
    WHERE
        c.club IS NOT NULL
), ai AS (
    SELECT
        p.*,
        {{ target.dataset }}.points(
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
            defensive_allowed_points_opponent_last_5
        ) AS expected_total_points,
        IF (status = 'expected', 1, 0) AS participate_proba
    FROM p
), club AS (
    SELECT
        club,
        all_time_round,
        AVG(expected_total_points * participate_proba) AS expected_total_points,
    FROM
        ai
    WHERE
        position != 'coach' AND participate_proba > 0.5
    GROUP BY
        club, all_time_round
)
SELECT
    ai.*,
    CASE
        WHEN ai.position = 'coach' THEN club.expected_total_points
        ELSE ai.expected_total_points * ai.participate_proba
    END AS adjusted_expected_total_points
FROM ai
LEFT JOIN club ON club.club = ai.club AND club.all_time_round = ai.all_time_round