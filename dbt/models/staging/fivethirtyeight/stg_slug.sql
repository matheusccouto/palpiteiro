SELECT
    s.name,
    s.slug
FROM
    {{ ref("slug") }} s
