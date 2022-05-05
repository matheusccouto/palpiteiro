SELECT
    CONCAT(
        RIGHT("temporada_id" :: TEXT, 2),
        CONCAT(
            LPAD("rodada_id" :: TEXT, 2, '0'),
            LPAD("atleta_id" :: TEXT, 6, '0')
        )
    ) :: INT AS "id",
    "atleta_id" :: INT AS "player",
    "rodada_id" :: INT AS "round",
    "temporada_id" :: INT AS "season",
    "clube_id" :: INT AS "club",
    "posicao_id" :: INT AS "position",
    "status_id" :: INT AS "status",
    "pontos_num" :: FLOAT AS "points",
    "preco_num" :: FLOAT AS "price",
    "variacao_num" :: FLOAT AS "variation",
    "media_num" :: FLOAT AS "mean",
    "jogos_num" :: INT AS "matches",
    COALESCE("G", 0) :: INT AS "goal",
    COALESCE("A", 0) :: INT AS "assist",
    COALESCE("CA", 0) :: INT AS "yellow_card",
    COALESCE("CV", 0) :: INT AS "red_card",
    COALESCE("FF", 0) :: INT AS "missed_shoot",
    COALESCE("FT", 0) :: INT AS "on_post_shoot",
    COALESCE("FD", 0) :: INT AS "saved_shoot",
    COALESCE("FS", 0) :: INT AS "received_foul",
    COALESCE("PS", 0) :: INT AS "received_penalty",
    COALESCE("PP", 0) :: INT AS "missed_penalty",
    COALESCE("I", 0) :: INT AS "outside",
    COALESCE("PE", 0) :: INT AS "missed_pass",
    CASE
        WHEN "RB" IS NULL THEN COALESCE("DS", 0) :: INT
        ELSE COALESCE("RB", 0) :: INT
    END AS "tackle",
    COALESCE("FC", 0) :: INT AS "foul",
    COALESCE("PC", 0) :: INT AS "penalty",
    COALESCE("GC", 0) :: INT AS "own_goal",
    COALESCE("GS", 0) :: INT AS "allowed_goal",
    COALESCE("SG", 0) :: INT AS "no_goal",
    COALESCE("DE", 0) :: INT AS "save",
    COALESCE("DD", 0) :: INT AS "difficult_save",
    COALESCE("DP", 0) :: INT AS "penalty_save"
FROM
    { { source('cartola', 'atletas') } }