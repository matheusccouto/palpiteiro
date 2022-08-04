SELECT
    id,
    club,
    position,
    price_cartola_express AS price,
    points AS actual_points,
FROM
    palpiteiro.fct_player
WHERE
    status == 'expected'
    AND position != 'coach'
    AND id IN {players_ids}