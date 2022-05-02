SELECT
    *
FROM
    cartola.atletas a
    LEFT JOIN cartola.partidas p ON a.temporada_id = p.temporada
    AND a.rodada_id = p.rodada