SELECT
    id,
    name,
    nickname,
    photo,
    COALESCE(
        slug,
        TRANSLATE(
            REPLACE(LOWER(nickname), ' ', '-'), 'áâãçéêíñóôõú', 'aaaceeinooou'
        )
    ) AS slug,
    COALESCE(
        short_nickname, REGEXP_REPLACE(TRIM(nickname), r'[a-z]+\s', '. ')
    ) AS short_nickname
FROM
    {{ ref ("stg_atletas_player") }}
