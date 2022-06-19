WITH club AS (
  SELECT
    s.club,
    s.all_time_round,
    ANY_VALUE(m.opponent) AS opponent,
    ANY_VALUE(m.home) AS home,
    ANY_VALUE(m.timestamp) AS timestamp,
    SUM(s.total_points) AS total_points,
    SUM(s.offensive_points) AS offensive_points,
    SUM(s.defensive_points) AS defensive_points
  FROM
    {{ ref("fct_scoring") }} s
    JOIN {{ ref ("fct_match") }} m ON s.all_time_round = m.all_time_round AND s.club = m.club
  GROUP BY
    club, all_time_round
)
SELECT
    c.club,
    c.all_time_round,
    c.home,
    c.opponent,
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
    AVG(c.total_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_club_last_5,
    AVG(c.offensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_club_last_5,
    AVG(c.defensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_club_last_5,
    AVG(o.total_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_allowed_points_opponent_last_5,
    AVG(o.offensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_allowed_points_opponent_last_5,
    AVG(o.defensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_allowed_points_opponent_last_5
FROM
    club c
    JOIN club o ON c.opponent = o.club AND c.all_time_round = o.all_time_round
    JOIN {{ ref ("fct_spi") }} s ON EXTRACT(DATE FROM c.timestamp AT TIME ZONE 'America/Sao_Paulo') = s.date AND c.club = s.club