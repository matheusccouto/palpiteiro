WITH player AS (
    SELECT
        *
    FROM
        {{ ref("fct_player") }}
    WHERE
        all_time_round = (
            SELECT
                MAX(all_time_round)
            FROM
                {{ ref("fct_match") }}
        )
),
ai AS (
    SELECT
        p.player,
        p.club,
        p.position,
        p.price,
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
        ) AS points,
        IF (p.status = 'expected', 1, 0) AS participate
    FROM
        player p
),
club_agg AS (
    SELECT
        club,
        AVG(points * participate) AS points,
    FROM
        ai
    WHERE
        position != 'coach'
        AND participate > 0.5
    GROUP BY
        club
)
SELECT
    dp.id,
    dp.short_nickname AS nickname,
    dp.photo,
    c.short_name AS club,
    c.badge60 AS badge,
    ai.position,
    ai.price,
    CASE
        WHEN ai.position = 'coach' THEN ca.points
        ELSE ai.points * ai.participate
    END AS points,
    ai.participate
FROM
    ai
    LEFT JOIN cartola.dim_player dp ON ai.player = dp.id
    LEFT JOIN cartola.stg_club c ON ai.club = c.slug
    LEFT JOIN club_agg ca ON ca.club = ai.club