WITH match AS (
    SELECT
        season,
        round,
        EXTRACT(
            DATE
            FROM
                timestamp
        ) AS timestamp,
        home,
        away
    FROM
        cartola.stg_partidas_match
),
spi AS (
    SELECT
        spi.*,
        cn1.id AS club_home,
        cn2.id AS club_away
    FROM
        fivethirtyeight.stg_spi_match spi
        LEFT JOIN cartola.clubs_names cn1 ON spi.home = cn1.name
        LEFT JOIN cartola.clubs_names cn2 ON spi.away = cn2.name
)
SELECT
    play.player,
    play.club,
    play.season,
    play.round,
    CASE
        WHEN play.position = 1 THEN 'goalkeeper'
        WHEN play.position = 2 THEN 'fullback'
        WHEN play.position = 3 THEN 'defender'
        WHEN play.position = 4 THEN 'midfielder'
        WHEN play.position = 5 THEN 'forward'
        WHEN play.position = 6 THEN 'coach'
        ELSE NULL
    END as position,
    CASE
        WHEN play.status = 2 THEN 'doubt'
        WHEN play.status = 3 THEN 'suspended'
        WHEN play.status = 5 THEN 'injured'
        WHEN play.status = 6 THEN 'null'
        WHEN play.status = 7 THEN 'expected'
        ELSE NULL
    END as status,
    play.points,
    play.price,
    play.variation,
    play.mean,
    play.matches,
    CASE
        WHEN COALESCE(prev.status, 6) = 2 THEN 'doubt'
        WHEN COALESCE(prev.status, 6) = 3 THEN 'suspended'
        WHEN COALESCE(prev.status, 6) = 5 THEN 'injured'
        WHEN COALESCE(prev.status, 6) = 6 THEN 'null'
        WHEN COALESCE(prev.status, 6) = 7 THEN 'expected'
        ELSE NULL
    END as status_prev,
    COALESCE(prev.points, 0) AS points_prev,
    COALESCE(prev.price, play.price) AS price_prev,
    COALESCE(prev.variation, 0) AS variation_prev,
    COALESCE(prev.mean, 0) AS mean_prev,
    COALESCE(prev.matches, 0) AS matches_prev,
    match.timestamp AS date,
    IF(
        play.club = spi.club_home,
        spi.spi_home,
        spi.spi_away
    ) AS spi,
    IF(
        play.club = spi.club_home,
        spi.spi_away,
        spi.spi_home
    ) AS spi_opp,
    IF(
        play.club = spi.club_home,
        spi.prob_home,
        spi.prob_away
    ) AS prob_win,
    IF(
        play.club = spi.club_home,
        spi.prob_away,
        spi.prob_home
    ) AS prob_lose,
    spi.prob_tie AS prob_tie,
    IF(
        play.club = spi.club_home,
        spi.proj_score_home,
        spi.proj_score_away
    ) AS proj_score,
    IF(
        play.club = spi.club_home,
        spi.proj_score_away,
        spi.proj_score_home
    ) AS proj_score_opp,
    IF(
        play.club = spi.club_home,
        spi.importance_home,
        spi.importance_away
    ) AS importance,
    IF(
        play.club = spi.club_home,
        spi.importance_away,
        spi.importance_home
    ) AS importance_opp
FROM
    cartola.stg_atletas_scoring play
    LEFT JOIN cartola.stg_atletas_scoring prev ON play.player = prev.player
    AND play.season = prev.season
    AND play.round = prev.round + 1
    LEFT JOIN match ON play.season = match.season
    AND play.round = match.round
    AND (
        play.club = match.home
        OR play.club = match.away
    )
    LEFT JOIN spi ON match.timestamp = spi.date
    AND (
        play.club = spi.club_home
        OR play.club = spi.club_away
    )