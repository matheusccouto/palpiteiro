SELECT
    CAST((temporada_id - 2000) * 100000000 + rodada_id * 1000000 + atleta_id AS int) AS id,
    CAST(atleta_id AS int) AS player,
    CAST(rodada_id AS int) AS round,
    CAST(temporada_id AS int) AS season,
    CAST(clube_id AS int) AS club,
    CAST(posicao_id AS int) AS position,
    CAST(status_id AS int) AS status,
    CAST(pontos_num AS DECIMAL) AS points,
    CAST(preco_num AS DECIMAL) AS price,
    CAST(variacao_num AS DECIMAL) AS variation,
    CAST(media_num AS DECIMAL) AS mean,
    CAST(COALESCE(jogos_num, 0) AS int) AS matches,
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
    {{ source ('cartola', 'atletas') }}
