WITH clubs AS (
  SELECT
    club,
    all_time_round,
    SUM(total_points) AS total_points,
    SUM(offensive_points) AS offensive_points,
    SUM(defensive_points) AS defensive_points
  FROM
    {{ ref(`fct_player`) }}
  GROUP BY
    club, all_time_round
),
opponents AS (
  SELECT
    c.club,
    c.all_time_round,
    c.total_points,
    c.offensive_points,
    c.defensive_points
  FROM
    {{ ref(`fct_player`) }} p
    JOIN clubs c ON p.opponent = c.club AND p.all_time_round = c.all_time_round
)
SELECT
  p.player,
  p.home,
  p.position,
  p.status,
  p.price_before,
  AVG(p.total_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_last_5,
  AVG(p.total_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS total_points_last_19,
  AVG(p.offensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_last_5,
  AVG(p.offensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS offensive_points_last_19,
  AVG(p.defensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_last_5,
  AVG(p.defensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS defensive_points_last_19,
  AVG(p.total_points_repr) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_repr_last_5,
  AVG(p.total_points_repr) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS total_points_repr_last_19,
  AVG(p.offensive_points_repr) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_repr_last_5,
  AVG(p.offensive_points_repr) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS offensive_points_repr_last_19,
  AVG(p.defensive_points_repr) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_repr_last_5,
  AVG(p.defensive_points_repr) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS defensive_points_repr_last_19,
  p.spi_club,
  p.spi_opponent,
  p.prob_club,
  p.prob_opponent,
  p.prob_tie,
  p.importance_club,
  p.importance_opponent,
  p.proj_score_club,
  p.proj_score_opponent,
  AVG(c.total_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_club_last_5,
  AVG(c.total_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS total_points_club_last_19,
  AVG(c.offensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_club_last_5,
  AVG(c.offensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS offensive_points_club_last_19,
  AVG(c.defensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_club_last_5,
  AVG(c.defensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS defensive_points_club_last_19,
  AVG(o.total_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_allowed_points_opponent_last_5,
  AVG(o.total_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS total_allowed_points_opponent_last_19,
  AVG(o.offensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_allowed_points_opponent_last_5,
  AVG(o.offensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS offensive_allowed_points_opponent_last_19,
  AVG(o.defensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_allowed_points_opponent_last_5,
  AVG(o.defensive_points) OVER (PARTITION BY p.home ORDER BY p.all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS defensive_allowed_points_opponent_last_19,
  p.total_points
FROM
  {{ ref(`fct_player`) }} p
  JOIN clubs c ON p.club = c.club AND p.all_time_round = c.all_time_round
  JOIN opponents o ON p.opponent = o.club AND p.all_time_round = o.all_time_round