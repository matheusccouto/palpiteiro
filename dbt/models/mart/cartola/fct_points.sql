WITH
  points AS (
  SELECT
    *,
    goal * 8 + 5 * assist + 3 * on_post_shoot + 1.2 * saved_shoot + 0.8 * missed_shoot + 0.5 * received_foul + 1 * received_penalty - 4 * missed_penalty - 0.1 * outside - 0.1 * missed_pass AS offensive,
    no_goal * 5 + penalty_save * 7 + save * 1 + tackle * 1.2 - own_goal * 3 - red_card * 3 - yellow_card * 1 - allowed_goal * 1 - foul * 0.3 - penalty * 1 AS defensive
  FROM
    {{ ref("stg_pontuados_scoring") }} ),
  players AS (
  SELECT
    id,
    player,
    round,
    season,
    club,
    position,
    ROUND(offensive, 1) AS offensive,
    ROUND(defensive, 1) AS defensive,
    ROUND(offensive + defensive, 1) AS total
  FROM
    points ),
  coaches AS (
  SELECT
    club,
    round,
    season,
    AVG(total) AS total
  FROM
    players
  GROUP BY
    club,
    season,
    round )
SELECT
  p.id,
  p.player,
  p.round,
  p.season,
  IF(p.position = 6, NULL, p.offensive) AS offensive,
  IF(p.position = 6, NULL, p.defensive) AS defensive,
  IF(p.position = 6, c.total, p.total) AS total,
FROM
  players p
LEFT JOIN
  coaches c
ON
  p.club = c.club
  AND p.round = c.round
  AND p.season = c.season