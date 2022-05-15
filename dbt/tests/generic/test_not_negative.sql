{% test not_negative (model, column_name) %} 

WITH validation AS (
    SELECT
        {{ column_name }} AS field
    FROM
        {{ model }}
),

validation_errors AS (
    SELECT
        field
    FROM
        validation
    WHERE
        field < 0
)
SELECT
    *
FROM
    validation_errors
    
{% endtest %}