WITH mat AS (
  SELECT
    season,
    round,
    38 * (season - 2017) + round AS all_time_round,
    timestamp,
    valid,
    c_home.slug AS club,
    c_away.slug AS opponent,
    TRUE AS home
  FROM
    {{ ref ('stg_partidas_match') }} m
    LEFT JOIN {{ ref ("stg_club") }} c_home ON home = c_home.id
    LEFT JOIN {{ ref ("stg_club") }} c_away ON away = c_away.id
),
inv AS (
  SELECT
    season,
    round,
    all_time_round,
    timestamp,
    valid,
    club AS opponent,
    opponent AS club,
    FALSE AS home
  FROM
    mat
)
SELECT
  season,
  round,
  all_time_round,
  timestamp,
  valid,
  club,
  opponent,
  home
FROM
  mat
UNION ALL
SELECT
  season,
  round,
  all_time_round,
  timestamp,
  valid,
  club,
  opponent,
  home
FROM
  inv
