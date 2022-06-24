WITH scoring AS (
    SELECT
        CAST(
            (
                temporada_id - 2000
            ) * 100000000 + rodada_id * 1000000 + atleta_id AS int
        ) AS id,
        CAST(atleta_id AS int) AS player,
        CAST(rodada_id AS int) AS round,
        CAST(temporada_id AS int) AS season,
        CAST(clube_id AS int) AS club,
        CAST(posicao_id AS int) AS position,
        CAST(status_id AS int) AS status,
        CAST(pontos_num AS decimal) AS points,
        CAST(preco_num AS decimal) AS price,
        CAST(variacao_num AS decimal) AS variation,
        CAST(media_num AS decimal) AS mean,
        CAST(COALESCE(jogos_num, 0) AS int) AS matches
    FROM
        {{ source("cartola", "atletas") }}
)

SELECT
    curr.id,
    curr.player,
    curr.round,
    curr.season,
    curr.club,
    curr.position,
    curr.points,
    curr.mean,
    curr.matches,
    CASE
        WHEN curr.season >= 2022 THEN curr.status
        ELSE prev.status
    END AS status,
    CASE
        WHEN curr.season >= 2022 THEN curr.price
        ELSE curr.price - curr.variation
    END AS price,
    CASE
        WHEN curr.season >= 2022 THEN curr.variation
        ELSE COALESCE(prev.variation, 0)
    END AS variation
FROM
    scoring AS curr
LEFT JOIN
    scoring AS prev ON
        curr.season = prev.season AND curr.round = prev.round + 1 AND curr.player = prev.player
