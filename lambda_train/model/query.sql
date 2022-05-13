SELECT
    player,
    club,
    season,
    round,
    position,
    IIF(points <= 0, 0, points) AS points_clipped,
    points,
    variation,
    status_prev,
    points_prev,
    price_prev,
    variation_prev,
    mean_prev,
    matches_prev,
    spi,
    spi_opp,
    prob_win,
    prob_lose,
    prob_tie,
    proj_score,
    proj_score_opp,
    importance,
    importance_opp
FROM
    palpiteiro.main
WHERE
    status = 'expected'
    AND season != 2020
    AND main.points != 0
