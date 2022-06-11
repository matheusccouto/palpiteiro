WITH scoring AS (
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
        CAST(COALESCE(jogos_num, 0) AS int) AS matches
    FROM
        {{ source("cartola", "atletas") }}
)
-- SELECT
--     *
-- FROM
--     scoring
SELECT
    curr.id,
    curr.player,
    curr.round,
    curr.season,
    curr.club,
    curr.position,
    CASE
        WHEN curr.season >= 2022 AND curr.round >= 10 THEN curr.status
        ELSE prev.status
    END AS status,
    curr.points,
    CASE
        WHEN curr.season >= 2022 AND curr.round >= 10 THEN curr.price
        ELSE curr.price - curr.variation
    END AS price,
    curr.variation,
    curr.mean,
    curr.matches
FROM
    scoring curr
    LEFT JOIN scoring prev ON curr.season = prev.season AND curr.round = prev.round + 1 AND curr.player = prev.player
