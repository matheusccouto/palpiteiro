WITH club AS (
    SELECT
        s.club,
        s.all_time_round,
        ANY_VALUE(m.opponent) AS opponent,
        ANY_VALUE(m.home) AS home,
        ANY_VALUE(m.timestamp) AS timestamp,
        COALESCE(ANY_VALUE(m.valid), SUM(s.total_points) IS NOT NULL) AS valid,
        SUM(s.total_points) AS total_points,
        SUM(s.offensive_points) AS offensive_points,
        SUM(s.defensive_points) AS defensive_points,
        SUM(s.goal) AS goal,
        SUM(s.assist) AS assist,
        SUM(s.yellow_card) AS yellow_card,
        SUM(s.red_card) AS red_card,
        SUM(s.missed_shoot) AS missed_shoot,
        SUM(s.on_post_shoot) AS on_post_shoot,
        SUM(s.saved_shoot) AS saved_shoot,
        SUM(s.received_foul) AS received_foul,
        SUM(s.received_penalty) AS received_penalty,
        SUM(s.missed_penalty) AS missed_penalty,
        SUM(s.outside) AS outside,
        SUM(s.missed_pass) AS missed_pass,
        SUM(s.tackle) AS tackle,
        SUM(s.foul) AS foul,
        SUM(s.penalty) AS penalty,
        SUM(s.own_goal) AS own_goal,
        SUM(s.allowed_goal) AS allowed_goal,
        SUM(s.no_goal) AS no_goal,
        SUM(s.save) AS save,
        SUM(s.penalty_save) AS penalty_save
    FROM
        {{ ref("fct_scoring") }} AS s
    INNER JOIN
        {{ ref ("fct_match") }} AS m ON
            s.all_time_round = m.all_time_round AND s.club = m.club
    GROUP BY
        club, all_time_round
)

SELECT
    c.club,
    c.all_time_round,
    c.timestamp,
    c.home,
    c.opponent,
    c.valid,
    COALESCE(SUM(CAST(c.valid AS INT64)) OVER (PARTITION BY c.club ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS valid_club_last_5,
    COALESCE(SUM(CAST(c.valid AS INT64)) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS valid_club_last_5_at,
    COALESCE(SUM(CAST(o.valid AS INT64)) OVER (PARTITION BY o.club ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS valid_opponent_last_5,
    COALESCE(SUM(CAST(o.valid AS INT64)) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS valid_opponent_last_5_at,
    s.spi_club,
    s.spi_opponent,
    s.prob_club,
    s.prob_opponent,
    s.prob_tie,
    s.importance_club,
    s.importance_opponent,
    s.proj_score_club,
    s.proj_score_opponent,
    c.total_points AS total_points_club,
    c.offensive_points AS offensive_points_club,
    c.defensive_points AS defensive_points_club,
    o.total_points AS total_points_opponent,
    o.offensive_points AS offensive_points_opponent,
    o.defensive_points AS defensive_points_opponent,
    SUM(c.total_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS total_points_club_last_5_at,
    SUM(c.offensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS offensive_points_club_last_5_at,
    SUM(c.defensive_points) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS defensive_points_club_last_5_at,
    SUM(o.total_points) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS total_allowed_points_opponent_last_5_at,
    SUM(o.offensive_points) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS offensive_allowed_points_opponent_last_5_at,
    SUM(o.defensive_points) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS defensive_allowed_points_opponent_last_5_at,
    COALESCE(SUM(c.goal) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS goals_club_last_5_at,
    COALESCE(SUM(c.assist) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS assists_club_last_5_at,
    COALESCE(SUM(c.yellow_card) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS yellow_cards_club_last_5_at,
    COALESCE(SUM(c.red_card) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS red_cards_club_last_5_at,
    COALESCE(SUM(c.missed_shoot) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS missed_shoots_club_last_5_at,
    COALESCE(SUM(c.on_post_shoot) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS on_post_shoots_club_last_5_at,
    COALESCE(SUM(c.saved_shoot) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS saved_shoots_club_last_5_at,
    COALESCE(SUM(c.received_foul) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS received_fouls_club_last_5_at,
    COALESCE(SUM(c.received_penalty) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS received_penalties_club_last_5_at,
    COALESCE(SUM(c.missed_penalty) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS missed_penalties_club_last_5_at,
    COALESCE(SUM(c.outside) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS outsides_club_last_5_at,
    COALESCE(SUM(c.missed_pass) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS missed_passes_club_last_5_at,
    COALESCE(SUM(c.tackle) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS tackles_club_last_5_at,
    COALESCE(SUM(c.foul) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS fouls_club_last_5_at,
    COALESCE(SUM(c.penalty) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS penalties_club_last_5_at,
    COALESCE(SUM(c.own_goal) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS own_goals_club_last_5_at,
    COALESCE(SUM(c.allowed_goal) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS allowed_goals_club_last_5_at,
    COALESCE(SUM(c.no_goal) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS no_goals_club_last_5_at,
    COALESCE(SUM(c.save) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS saves_club_last_5_at,
    COALESCE(SUM(c.penalty_save) OVER (PARTITION BY c.club, c.home ORDER BY c.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS penalty_saves_club_last_5_at,
    COALESCE(SUM(o.goal) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS goals_opponent_last_5_at,
    COALESCE(SUM(o.assist) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS assists_opponent_last_5_at,
    COALESCE(SUM(o.yellow_card) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS yellow_cards_opponent_last_5_at,
    COALESCE(SUM(o.red_card) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS red_cards_opponent_last_5_at,
    COALESCE(SUM(o.missed_shoot) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS missed_shoots_opponent_last_5_at,
    COALESCE(SUM(o.on_post_shoot) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS on_post_shoots_opponent_last_5_at,
    COALESCE(SUM(o.saved_shoot) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS saved_shoots_opponent_last_5_at,
    COALESCE(SUM(o.received_foul) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS received_fouls_opponent_last_5_at,
    COALESCE(SUM(o.received_penalty) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS received_penalties_opponent_last_5_at,
    COALESCE(SUM(o.missed_penalty) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS missed_penalties_opponent_last_5_at,
    COALESCE(SUM(o.outside) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS outsides_opponent_last_5_at,
    COALESCE(SUM(o.missed_pass) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS missed_passes_opponent_last_5_at,
    COALESCE(SUM(o.tackle) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS tackles_opponent_last_5_at,
    COALESCE(SUM(o.foul) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS fouls_opponent_last_5_at,
    COALESCE(SUM(o.penalty) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS penalties_opponent_last_5_at,
    COALESCE(SUM(o.own_goal) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS own_goals_opponent_last_5_at,
    COALESCE(SUM(o.allowed_goal) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS allowed_goals_opponent_last_5_at,
    COALESCE(SUM(o.no_goal) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS no_goals_opponent_last_5_at,
    COALESCE(SUM(o.save) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS saves_opponent_last_5_at,
    COALESCE(SUM(o.penalty_save) OVER (PARTITION BY o.club, o.home ORDER BY o.all_time_round ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING), 0) AS penalty_saves_opponent_last_5_at,
    h2h.pinnacle_club AS pinnacle_odds_club,
    h2h.pinnacle_opponent AS pinnacle_odds_opponent,
    h2h.pinnacle_draw AS pinnacle_odds_draw,
    h2h.max_club AS max_odds_club,
    h2h.max_opponent AS max_odds_opponent,
    h2h.max_draw AS max_odds_draw,
    h2h.avg_club AS avg_odds_club,
    h2h.avg_opponent AS avg_odds_opponent,
    h2h.avg_draw AS avg_odds_draw,
FROM
    club AS c
INNER JOIN
    club AS o ON c.opponent = o.club AND c.all_time_round = o.all_time_round
INNER JOIN
    {{ ref ("fct_spi") }} AS s ON EXTRACT(DATE FROM c.timestamp AT TIME ZONE 'America/Sao_Paulo') = s.date AND c.club = s.club
INNER JOIN
    {{ ref ("fct_h2h") }} AS h2h ON EXTRACT(DATE FROM h2h.timestamp AT TIME ZONE 'America/Sao_Paulo') = s.date AND c.club = h2h.club
