SELECT
    *
FROM
    {{ ref("dim_player_last") }} p
WHERE
    EXTRACT(DATE FROM p.timestamp AT TIME ZONE 'America/Sao_Paulo') = CURRENT_DATE('America/Sao_Paulo')