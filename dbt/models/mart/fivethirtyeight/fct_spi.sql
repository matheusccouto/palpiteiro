WITH spi AS (
    SELECT
        season,
        date,
        league_id,
        league,
        slug_home.slug AS club,
        slug_away.slug AS opponent,
        spi_home AS spi_club,
        spi_away AS spi_opponent,
        prob_home AS prob_club,
        prob_away AS prob_opponent,
        prob_tie,
        COALESCE(importance_home, AVG(importance_home) OVER (PARTITION BY EXTRACT(WEEK FROM date))) AS importance_club,
        COALESCE(importance_away, AVG(importance_away) OVER (PARTITION BY EXTRACT(WEEK FROM date))) AS importance_opponent,
        proj_score_home AS proj_score_club,
        proj_score_away AS proj_score_opponent,
        score_home AS score_club,
        score_away AS score_opponent,
        adj_score_home AS adj_score_club,
        adj_score_away AS adj_score_opponent,
        xg_home AS xg_club,
        xg_away AS xg_opponent,
        nsxg_home AS nsxg_club,
        nsxg_away AS nsxg_opponent
    FROM
        {{ ref ("stg_spi_match") }} spi
        LEFT JOIN {{ ref ("stg_spi_slug") }} slug_home ON spi.home = slug_home.name
        LEFT JOIN {{ ref ("stg_spi_slug") }} slug_away ON spi.away = slug_away.name
),
inv AS (
    SELECT
        season,
        date,
        club AS opponent,
        opponent AS club,
        spi_club AS spi_opponent,
        spi_opponent AS spi_club,
        prob_club AS prob_opponent,
        prob_opponent AS prob_club,
        prob_tie,
        importance_club AS importance_opponent,
        importance_opponent AS importance_club,
        proj_score_club AS proj_score_opponent,
        proj_score_opponent AS proj_score_club,
        score_club AS score_opponent,
        score_opponent AS score_club,
        adj_score_club AS adj_score_opponent,
        adj_score_opponent AS adj_score_club,
        xg_club AS xg_opponent,
        xg_opponent AS xg_club,
        nsxg_club AS nsxg_opponent,
        nsxg_opponent AS nsxg_club
    FROM
        spi
)
SELECT
    season,
    date,
    club,
    opponent,
    spi_club,
    spi_opponent,
    prob_club,
    prob_opponent,
    prob_tie,
    importance_club,
    importance_opponent,
    proj_score_club,
    proj_score_opponent,
    score_club,
    score_opponent,
    adj_score_club,
    adj_score_opponent,
    xg_club,
    xg_opponent,
    nsxg_club,
    nsxg_opponent
FROM
    spi
UNION ALL
SELECT
    season,
    date,
    club,
    opponent,
    spi_club,
    spi_opponent,
    prob_club,
    prob_opponent,
    prob_tie,
    importance_club,
    importance_opponent,
    proj_score_club,
    proj_score_opponent,
    score_club,
    score_opponent,
    adj_score_club,
    adj_score_opponent,
    xg_club,
    xg_opponent,
    nsxg_club,
    nsxg_opponent
FROM
    inv
