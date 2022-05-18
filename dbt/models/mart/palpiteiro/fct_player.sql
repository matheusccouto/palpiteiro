SELECT
    score.player,
    score.name,
    score.season,
    score.round,
    score.all_time_round,
    mat.timestamp,
    mat.valid,
    score.club,
    mat.opponent,
    mat.home,
    score.position,
    score.status,
    score.points,
    score.price,
    score.price - score.variation AS price_before,
    score.variation,
    score.mean,
    score.matches,
    spi.spi_club,
    spi.spi_opponent,
    spi.prob_club,
    spi.prob_opponent,
    spi.prob_tie,
    spi.importance_club,
    spi.importance_opponent,
    spi.proj_score_club,
    spi.proj_score_opponent,
    spi.score_club,
    spi.score_opponent,
    spi.adj_score_club,
    spi.adj_score_opponent,
    spi.xg_club,
    spi.xg_opponent,
    spi.nsxg_club,
    spi.nsxg_opponent,
    score.goal,
    score.assist,
    score.yellow_card,
    score.red_card,
    score.missed_shoot,
    score.on_post_shoot,
    score.saved_shoot,
    score.received_foul,
    score.received_penalty,
    score.missed_penalty,
    score.outside,
    score.missed_pass,
    score.tackle,
    score.foul,
    score.penalty,
    score.own_goal,
    score.allowed_goal,
    score.no_goal,
    score.save,
    score.difficult_save,
    score.penalty_save
FROM
    {{ ref ("fct_scoring") }} score
    LEFT JOIN {{ ref ("fct_match") }} mat ON score.season = mat.season
        AND score.round = mat.round
        AND score.club = mat.club
    LEFT JOIN {{ ref ("fct_spi") }} spi ON EXTRACT(DATE FROM mat.timestamp AT TIME ZONE 'America/Sao_Paulo') = spi.date
        AND mat.club = spi.club
