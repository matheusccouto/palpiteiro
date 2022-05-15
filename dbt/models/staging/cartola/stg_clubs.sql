SELECT
    id,
    slug AS slug,
    nome AS name,
    abreviacao AS short_name,
    escudo_60x60 AS badge60,
    escudo_45x45 AS badge45,
    escudo_30x30 AS badge30,
    nome_fantasia AS fantasy_name
FROM
    {{ ref ("clubs") }}
