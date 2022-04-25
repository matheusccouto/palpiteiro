CREATE VIEW palpiteiro.main AS WITH match AS (
    SELECT
        season,
        round,
        DATEADD(
            dd,
            DATEDIFF(dd, 0, date),
            0
        ) AS date,
        home,
        away
    FROM
        cartola.match
),
spi AS (
    SELECT
        spim.*,
        cn1.id AS club1,
        cn2.id AS club2
    FROM
        spi.match spim
        LEFT JOIN cartola.club_name cn1 ON spim.team1 = cn1.name
        LEFT JOIN cartola.club_name cn2 ON spim.team2 = cn2.name
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
    match.date AS date,
    IIF(play.club = spi.club1, spi.spi1, spi.spi2) AS spi,
    IIF(play.club = spi.club1, spi.spi2, spi.spi1) AS spi_opp,
    IIF(play.club = spi.club1, spi.prob1, spi.prob2) AS prob_win,
    IIF(play.club = spi.club1, spi.prob2, spi.prob1) AS prob_lose,
    spi.probtie AS prob_tie,
    IIF(
        play.club = spi.club1,
        spi.proj_score1,
        spi.proj_score2
    ) AS proj_score,
    IIF(
        play.club = spi.club1,
        spi.proj_score2,
        spi.proj_score1
    ) AS proj_score_opp,
    IIF(
        play.club = spi.club1,
        spi.importance1,
        spi.importance2
    ) AS importance,
    IIF(
        play.club = spi.club1,
        spi.importance2,
        spi.importance1
    ) AS importance_opp
FROM
    cartola.play play
    LEFT JOIN cartola.play prev ON play.player = prev.player
    AND play.season = prev.season
    AND play.round = prev.round + 1
    LEFT JOIN match ON play.season = match.season
    AND play.round = match.round
    AND (
        play.club = match.home
        OR play.club = match.away
    )
    LEFT JOIN spi ON match.date = spi.date
    AND (
        play.club = spi.club1
        OR play.club = spi.club2
    )