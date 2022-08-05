SELECT
    id AS play_id,
    player AS id,
    club,
    position,
    all_time_round,
    price_cartola_express AS price,
    total_points AS actual_points,
FROM
    palpiteiro.fct_player
WHERE
    status = 'expected'
    AND position != 'coach'
    AND id IN ({players_ids})