SELECT
    sc.id,
    pl.id AS player,
    pl.nickname AS name,
    sc.round,
    sc.season,
    38 * (sc.season - 2017) + sc.round AS all_time_round,
    c.slug AS club,
    po.slug AS position,
    st.slug AS status,
    sc.points,
    sc.price,
    sc.variation,
    sc.mean,
    sc.matches,
    pt.goal  AS goal,
    pt.assist AS assist,
    pt.yellow_card AS yellow_card,
    pt.red_card AS red_card,
    pt.missed_shoot AS missed_shoot,
    pt.on_post_shoot AS on_post_shoot,
    pt.saved_shoot AS saved_shoot,
    pt.received_foul AS received_foul,
    pt.received_penalty AS received_penalty,
    pt.missed_penalty AS missed_penalty,
    pt.outside AS outside,
    pt.missed_pass AS missed_pass,
    pt.tackle AS tackle,
    pt.foul AS foul,
    pt.penalty AS penalty,
    pt.own_goal AS own_goal,
    pt.allowed_goal AS allowed_goal,
    pt.no_goal AS no_goal,
    pt.save AS save,
    pt.difficult_save AS difficult_save,
    pt.penalty_save AS penalty_save,
FROM
    {{ ref ("stg_atletas_scoring") }} sc
    LEFT JOIN {{ ref ("stg_pontuados_scoring") }} pt ON sc.id = pt.id
    LEFT JOIN {{ ref ("dim_player") }} pl ON sc.player = pl.id
    LEFT JOIN {{ ref ("stg_positions") }} po ON sc.position = po.id
    LEFT JOIN {{ ref ("stg_status") }} st ON status = st.id
    LEFT JOIN {{ ref ("stg_clubs") }} c ON sc.club = c.id
WHERE
    c.slug <> "other"