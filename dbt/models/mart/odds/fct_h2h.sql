WITH h2h AS (
    SELECT
        h2h.id,
        h2h.season,
        h2h.timestamp,
        h.slug AS club,
        a.slug AS opponent,
        h2h.pinnacle_home AS pinnacle_club,
        h2h.pinnacle_away AS pinnacle_opponent,
        h2h.pinnacle_draw AS pinnacle_draw,
        h2h.max_home AS max_club,
        h2h.max_away AS max_opponent,
        h2h.max_draw AS max_draw,
        h2h.avg_home AS avg_club,
        h2h.avg_away AS avg_opponent,
        h2h.avg_draw AS avg_draw
    FROM
        {{ ref("stg_brasileirao_h2h") }} h2h
        LEFT JOIN {{ ref("dim_slug") }} AS h ON h.name = h2h.home
        LEFT JOIN {{ ref("dim_slug") }} AS a ON a.name = h2h.away
),
inv AS (
    SELECT
        id,
        season,
        timestamp,
        opponent AS club,
        club AS opponent,
        pinnacle_opponent AS pinnacle_club,
        pinnacle_club AS pinnacle_opponent,
        pinnacle_draw,
        max_opponent AS max_club,
        max_club AS max_opponent,
        max_draw,
        avg_opponent AS avg_club,
        avg_club AS avg_opponent,
        avg_draw
    FROM
        h2h
)
SELECT
    id,
    season,
    timestamp,
    club,
    opponent,
    pinnacle_club,
    pinnacle_opponent,
    pinnacle_draw,
    max_club,
    max_opponent,
    max_draw,
    avg_club,
    avg_opponent,
    avg_draw
FROM 
    h2h
UNION ALL
SELECT
    id,
    season,
    timestamp,
    club,
    opponent,
    pinnacle_club,
    pinnacle_opponent,
    pinnacle_draw,
    max_club,
    max_opponent,
    max_draw,
    avg_club,
    avg_opponent,
    avg_draw
FROM
    inv