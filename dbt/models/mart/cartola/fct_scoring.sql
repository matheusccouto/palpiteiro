WITH scout AS (
    SELECT
        s.*,
        {{ target.dataset }}.offensive_points_cartola(
            p.slug,
            s.goal,
            s.assist,
            s.yellow_card,
            s.red_card,
            s.missed_shoot,
            s.on_post_shoot,
            s.saved_shoot,
            s.received_foul,
            s.received_penalty,
            s.missed_penalty,
            s.outside,
            s.missed_pass,
            s.tackle,
            s.foul,
            s.penalty,
            s.own_goal,
            s.allowed_goal,
            s.no_goal,
            s.save,
            s.penalty_save
        ) AS offensive,
        {{ target.dataset }}.defensive_points_cartola(
            p.slug,
            s.goal,
            s.assist,
            s.yellow_card,
            s.red_card,
            s.missed_shoot,
            s.on_post_shoot,
            s.saved_shoot,
            s.received_foul,
            s.received_penalty,
            s.missed_penalty,
            s.outside,
            s.missed_pass,
            s.tackle,
            s.foul,
            s.penalty,
            s.own_goal,
            s.allowed_goal,
            s.no_goal,
            s.save,
            s.penalty_save
        ) AS defensive
    FROM
        {{ ref("stg_pontuados_scoring") }} s
        LEFT JOIN {{ ref("dim_position") }} p ON s.position = p.id
),

point AS (
    SELECT
        id,
        player,
        round,
        season,
        played,
        IF(played IS TRUE, ROUND(offensive, 1), NULL) AS offensive,
        IF(played IS TRUE, ROUND(defensive, 1), NULL) AS defensive,
        IF(played IS TRUE, ROUND(offensive + defensive, 1), NULL) AS total
    FROM
        scout
)

SELECT
    sc1.id,
    pl.id AS player,
    pl.nickname AS name,
    sc1.round,
    sc1.season,
    c.slug AS club,
    po.slug AS position,
    st.slug AS status,
    pt.total AS total_points,
    pt.offensive AS offensive_points,
    pt.defensive AS defensive_points,
    sc1.price,
    sc1.variation,
    sc1.matches,
    pt.played,
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
    sc2.penalty_save AS penalty_save,
    38 * (sc1.season - 2017) + sc1.round AS all_time_round
FROM
    {{ ref ("stg_atletas_scoring") }} AS sc1
LEFT JOIN {{ ref ("stg_pontuados_scoring") }} AS sc2 ON sc1.id = sc2.id
LEFT JOIN point AS pt ON sc1.id = pt.id
LEFT JOIN {{ ref ("dim_player") }} AS pl ON sc1.player = pl.id
LEFT JOIN {{ ref ("dim_position") }} AS po ON sc1.position = po.id
LEFT JOIN {{ ref ("dim_status") }} AS st ON status = st.id
LEFT JOIN {{ ref ("dim_club") }} AS c ON sc1.club = c.id
WHERE
    c.slug != "other"
