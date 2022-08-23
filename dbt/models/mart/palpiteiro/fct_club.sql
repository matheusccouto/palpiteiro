WITH club AS (
    SELECT
        s.club,
        s.all_time_round,
        ANY_VALUE(m.opponent) AS opponent,
        ANY_VALUE(m.home) AS home,
        ANY_VALUE(m.timestamp) AS timestamp,
        ANY_VALUE(m.valid) AS valid,
        SUM(s.total_points) AS total_points,
        SUM(s.offensive_points) AS offensive_points,
        SUM(s.defensive_points) AS defensive_points,
        SUM(s.penalty) AS penalties,
        SUM(s.received_penalty) AS received_penalties
    FROM
        {{ ref("fct_scoring") }} AS s
    INNER JOIN
        {{ ref ("fct_match") }} AS m ON
            s.all_time_round = m.all_time_round AND s.club = m.club
    GROUP BY
        club, all_time_round
)

SELECT
    c.club,
    c.all_time_round,
    c.timestamp,
    c.home,
    c.opponent,
    c.valid,
    COALESCE(SUM(CAST(c.valid AS INT64)) OVER (PARTITION BY c.club ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS valid_last_5,
    COALESCE(SUM(CAST(c.valid AS INT64)) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS valid_last_5_at
    s.spi_club,
    s.spi_opponent,
    s.prob_club,
    s.prob_opponent,
    s.prob_tie,
    s.importance_club,
    s.importance_opponent,
    s.proj_score_club,
    s.proj_score_opponent,
    c.total_points AS total_points_club,
    c.offensive_points AS offensive_points_club,
    c.defensive_points AS defensive_points_club,
    o.total_points AS total_points_opponent,
    o.offensive_points AS offensive_points_opponent,
    o.defensive_points AS defensive_points_opponent,
    SUM(c.total_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_club_last_5,
    SUM(c.offensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_club_last_5,
    SUM(c.defensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_club_last_5,
    SUM(o.total_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_allowed_points_opponent_last_5,
    SUM(o.offensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_allowed_points_opponent_last_5,
    SUM(o.defensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_allowed_points_opponent_last_5,
    COALESCE(AVG(c.penalties) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING), 0) AS penalties_club_last_5,
    COALESCE(AVG(o.penalties) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING), 0) AS penalties_opponent_last_5,
    COALESCE(AVG(c.received_penalties) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING), 0) AS received_penalties_club_last_5,
    COALESCE(AVG(o.received_penalties) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING), 0) AS received_penalties_opponent_last_5,
    h2h.pinnacle_club AS pinnacle_odds_club,
    h2h.pinnacle_opponent AS pinnacle_odds_opponent,
    h2h.pinnacle_draw AS pinnacle_odds_draw,
    h2h.max_club AS max_odds_club,
    h2h.max_opponent AS max_odds_opponent,
    h2h.max_draw AS max_odds_draw,
    h2h.avg_club AS avg_odds_club,
    h2h.avg_opponent AS avg_odds_opponent,
    h2h.avg_draw AS avg_odds_draw,
FROM
    club AS c
INNER JOIN
    club AS o ON c.opponent = o.club AND c.all_time_round = o.all_time_round
INNER JOIN
    {{ ref ("fct_spi") }} AS s ON EXTRACT(DATE FROM c.timestamp AT TIME ZONE 'America/Sao_Paulo') = s.date AND c.club = s.club
INNER JOIN
    {{ ref ("fct_h2h") }} AS h2h ON EXTRACT(DATE FROM h2h.timestamp AT TIME ZONE 'America/Sao_Paulo') = s.date AND c.club = h2h.club
