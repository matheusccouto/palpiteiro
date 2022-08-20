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
        ) AND valid IS TRUE
),
ai AS (
    SELECT
        p.id,
        p.player,
        p.club,
        p.timestamp,
        p.position,
        p.price_cartola,
        p.price_cartola_express,
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
            defensive_allowed_points_opponent_last_5,
            penalties_club_last_5,
            penalties_opponent_last_5,
            received_penalties_club_last_5,
            received_penalties_opponent_last_5,
            played_last_5
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
),
expected_to_play AS (
    SELECT
        *
    FROM
        ai
    WHERE
        participate > 0.5
)
SELECT
    e2p.player,
    e2p.timestamp,
    dp.short_nickname AS name,
    dp.photo,
    c.id AS club,
    c.short_name AS club_name,
    c.badge60 AS club_badge,
    e2p.position,
    e2p.price_cartola,
    e2p.price_cartola_express,
    CASE
        WHEN e2p.position = 'coach' THEN round(ca.points, 2)
        ELSE round(e2p.points * e2p.participate, 2)
    END AS points,
    current_timestamp AS materialized_at
FROM
    expected_to_play e2p
    LEFT JOIN {{ ref("dim_player") }} dp ON e2p.player = dp.id
    LEFT JOIN {{ ref("dim_club") }} c ON e2p.club = c.slug
    LEFT JOIN club_agg ca ON ca.club = e2p.club