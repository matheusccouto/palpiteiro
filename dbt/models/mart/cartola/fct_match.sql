SELECT
  id,
  season,
  round,
  timestamp,
  valid,
  home,
  away
FROM
  {{ ref.stg_partidas_match }}