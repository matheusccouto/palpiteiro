SELECT
    CAST((temporada - 2000) * 100000000 + rodada * 1000000 + id AS int) AS id,
    CAST(id AS int) AS player,
    CAST(rodada AS int) AS round,
    CAST(temporada AS int) AS season,
    CAST(clube_id AS int) AS club,
    CAST(posicao_id AS int) AS position,
    CASE WHEN posicao_id = 6 THEN
        FALSE
        ELSE
            CAST(COALESCE(entrou_em_campo, pontuacao != 0) AS boolean)
    END AS played,
    CAST(pontuacao AS decimal) AS points,
    CAST(COALESCE(g, 0) AS int) AS goal,
    CAST(COALESCE(a, 0) AS int) AS assist,
    CAST(COALESCE(ca, 0) AS int) AS yellow_card,
    CAST(COALESCE(cv, 0) AS int) AS red_card,
    CAST(COALESCE(ff, 0) AS int) AS missed_shoot,
    CAST(COALESCE(ft, 0) AS int) AS on_post_shoot,
    CAST(COALESCE(fd, 0) AS int) AS saved_shoot,
    CAST(COALESCE(fs, 0) AS int) AS received_foul,
    CAST(COALESCE(ps, 0) AS int) AS received_penalty,
    CAST(COALESCE(pp, 0) AS int) AS missed_penalty,
    CAST(COALESCE(i, 0) AS int) AS outside,
    CASE WHEN pe IS NULL THEN
        CAST(COALESCE(pi, 0) AS int)
        ELSE
            CAST(COALESCE(pe, 0) AS int)
    END AS missed_pass,
    CASE WHEN rb IS NULL THEN
        CAST(COALESCE(ds, 0) AS int)
        ELSE
            CAST(COALESCE(rb, 0) AS int)
    END AS tackle,
    CAST(COALESCE(fc, 0) AS int) AS foul,
    CAST(COALESCE(pc, 0) AS int) AS penalty,
    CAST(COALESCE(gc, 0) AS int) AS own_goal,
    CAST(COALESCE(gs, 0) AS int) AS allowed_goal,
    CAST(COALESCE(sg, 0) AS int) AS no_goal,
    CAST(COALESCE(de, 0) AS int) AS save,
    CAST(COALESCE(dd, 0) AS int) AS difficult_save,
    CAST(COALESCE(dp, 0) AS int) AS penalty_save
FROM
    {{ source ('cartola', 'pontuados') }}
