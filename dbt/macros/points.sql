{% macro points_cartola() %}

CREATE OR REPLACE FUNCTION {{ target.dataset }}.offensive_points_cartola(
    position STRING,
    goal INT,
    assist INT,
    yellow_card INT,
    red_card INT,
    missed_shoot INT,
    on_post_shoot INT,
    saved_shoot INT,
    received_foul INT,
    received_penalty INT,
    missed_penalty INT,
    outside INT,
    missed_pass INT,
    tackle INT,
    foul INT,
    penalty INT,
    own_goal INT,
    allowed_goal INT,
    no_goal INT,
    save INT,
    penalty_save INT
) RETURNS FLOAT64 AS (
    8.0 * goal 
    + 5.0 * assist 
    + 3.0 * on_post_shoot 
    + 1.2 * saved_shoot 
    + 0.8 * missed_shoot 
    + 0.5 * received_foul 
    + 1.0 * received_penalty 
    - 4.0 * missed_penalty 
    - 0.1 * outside
    - IF(position != 'goalkeeper', 0.1 * missed_pass, 0.0)
);

CREATE OR REPLACE FUNCTION {{ target.dataset }}.defensive_points_cartola(
    position STRING,
    goal INT,
    assist INT,
    yellow_card INT,
    red_card INT,
    missed_shoot INT,
    on_post_shoot INT,
    saved_shoot INT,
    received_foul INT,
    received_penalty INT,
    missed_penalty INT,
    outside INT,
    missed_pass INT,
    tackle INT,
    foul INT,
    penalty INT,
    own_goal INT,
    allowed_goal INT,
    no_goal INT,
    save INT,
    penalty_save INT
) RETURNS FLOAT64 AS (
    IF(position IN ('goalkeeper', 'defender', 'fullback'), 5.0 * no_goal, 0.0)
    + IF(position = 'goalkeeper', 7.0 * penalty_save, 0.0)
    + IF(position = 'goalkeeper', 1.0 * save, 0.0)
    - IF(position = 'goalkeeper', 1.0 * allowed_goal, 0.0)
    + 1.2 * tackle 
    - 3.0 * own_goal
    - 3.0 * red_card 
    - 1.0 * yellow_card 
    - 0.3 * foul 
    - 1.0 * penalty
);

{% endmacro %}