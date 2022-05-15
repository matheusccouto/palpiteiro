SELECT
    name,
    slug
FROM
    {{ ref ("spi_slugs") }}
