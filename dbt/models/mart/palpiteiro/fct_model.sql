SELECT
  player,
  home,
  position,
  status,
  price_before,
  AVG(total_points) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_last_5,
  AVG(total_points) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS total_points_last_19,
  AVG(offensive_points) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_last_5,
  AVG(offensive_points) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS offensive_points_last_19,
  AVG(defensive_points) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_last_5,
  AVG(defensive_points) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS defensive_points_last_19,
  AVG(total_points_repr) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS total_points_repr_last_5,
  AVG(total_points_repr) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS total_points_repr_last_19,
  AVG(offensive_points_repr) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS offensive_points_repr_last_5,
  AVG(offensive_points_repr) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS offensive_points_repr_last_19,
  AVG(defensive_points_repr) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS defensive_points_repr_last_5,
  AVG(defensive_points_repr) OVER (PARTITION BY home ORDER BY all_time_round ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS defensive_points_repr_last_19,
  spi_club,
  spi_opponent,
  prob_club,
  prob_opponent,
  prob_tie,
  importance_club,
  importance_opponent,
  proj_score_club,
  proj_score_opponent,
  total_points
FROM
  {{ ref("fct_player") }}
WHERE
  name = 'Cano'
ORDER BY
  all_time_round DESC