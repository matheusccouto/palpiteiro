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
        CAST(COALESCE(entrou_em_campo, pontuacao <> 0) AS boolean)
    END AS played,
    CAST(pontuacao AS DECIMAL) AS points,
    CAST(COALESCE(G, 0) AS int) AS goal,
    CAST(COALESCE(A, 0) AS int) AS assist,
    CAST(COALESCE(CA, 0) AS int) AS yellow_card,
    CAST(COALESCE(CV, 0) AS int) AS red_card,
    CAST(COALESCE(FF, 0) AS int) AS missed_shoot,
    CAST(COALESCE(FT, 0) AS int) AS on_post_shoot,
    CAST(COALESCE(FD, 0) AS int) AS saved_shoot,
    CAST(COALESCE(FS, 0) AS int) AS received_foul,
    CAST(COALESCE(PS, 0) AS int) AS received_penalty,
    CAST(COALESCE(PP, 0) AS int) AS missed_penalty,
    CAST(COALESCE(I, 0) AS int) AS outside,
    CASE WHEN PE IS NULL THEN
        CAST(COALESCE(PI, 0) AS int)
    ELSE
        CAST(COALESCE(PE, 0) AS int)
    END AS missed_pass,
    CASE WHEN RB IS NULL THEN
        CAST(COALESCE(DS, 0) AS int)
    ELSE
        CAST(COALESCE(RB, 0) AS int)
    END AS tackle,
    CAST(COALESCE(FC, 0) AS int) AS foul,
    CAST(COALESCE(PC, 0) AS int) AS penalty,
    CAST(COALESCE(GC, 0) AS int) AS own_goal,
    CAST(COALESCE(GS, 0) AS int) AS allowed_goal,
    CAST(COALESCE(SG, 0) AS int) AS no_goal,
    CAST(COALESCE(DE, 0) AS int) AS save,
    CAST(COALESCE(DD, 0) AS int) AS difficult_save,
    CAST(COALESCE(DP, 0) AS int) AS penalty_save
FROM
    {{ source ('cartola', 'pontuados') }}
