SELECT
    sc1.id,
    pl.id AS player,
    pl.nickname AS name,
    sc1.round,
    sc1.season,
    38 * (sc1.season - 2017) + sc1.round AS all_time_round,
    c.slug AS club,
    po.slug AS position,
    st.slug AS status,
    pt.total AS total_points,
    pt.offensive AS offensive_points,
    pt.defensive AS defensive_points,
    pt.total_repr AS total_points_repr,
    pt.offensive_repr AS offensive_points_repr,
    pt.defensive_repr AS defensive_points_repr,
    sc1.price,
    sc1.price - sc1.variation AS price_before,
    sc1.matches,
    sc2.goal AS goal,
    sc2.assist AS assist,
    sc2.yellow_card AS yellow_card,
    sc2.red_card AS red_card,
    sc2.missed_shoot AS missed_shoot,
    sc2.on_post_shoot AS on_post_shoot,
    sc2.saved_shoot AS saved_shoot,
    sc2.received_foul AS received_foul,
    sc2.received_penalty AS received_penalty,
    sc2.missed_penalty AS missed_penalty,
    sc2.outside AS outside,
    sc2.missed_pass AS missed_pass,
    sc2.tackle AS tackle,
    sc2.foul AS foul,
    sc2.penalty AS penalty,
    sc2.own_goal AS own_goal,
    sc2.allowed_goal AS allowed_goal,
    sc2.no_goal AS no_goal,
    sc2.save AS save,
    sc2.difficult_save AS difficult_save,
    sc2.penalty_save AS penalty_save,
FROM
    {{ ref ("stg_atletas_scoring") }} sc1
    LEFT JOIN {{ ref ("stg_pontuados_scoring") }} sc2 ON sc1.id = sc2.id
    LEFT JOIN {{ ref ("fct_point") }} pt ON sc1.id = pt.id
    LEFT JOIN {{ ref ("dim_player") }} pl ON sc1.player = pl.id
    LEFT JOIN {{ ref ("stg_position") }} po ON sc1.position = po.id
    LEFT JOIN {{ ref ("stg_status") }} st ON status = st.id
    LEFT JOIN {{ ref ("stg_club") }} c ON sc1.club = c.id
WHERE
    c.slug <> "other"
