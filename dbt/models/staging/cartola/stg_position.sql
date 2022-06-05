SELECT
    id,
    slug AS slug,
    nome AS name,
    abreviacao AS short_name
FROM
    {{ ref ("position") }}
