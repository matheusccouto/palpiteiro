CREATE VIEW palpiteiro.model AS
SELECT
    season,
    round,
    position,
    points,
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
    status = 7
    AND points != 0