SELECT
  id,
  COALESCE(slug, TRANSLATE(REPLACE(LOWER(nickname), ' ', '-'), 'áâãçéêíñóôõú', 'aaaceeinooou')) AS slug,
  name,
  nickname,
  COALESCE(short_nickname, REGEXP_REPLACE(TRIM(nickname), r'[a-z]+\s', '. ')) AS short_nickname,
  photo
FROM
  {{ ref ("stg_atletas_player") }}
