SELECT
    id,
    slug AS slug,
    nome AS name
FROM
    {{ ref ("status") }}
