{% macro create_udfs() %}

{% do run_query(predict_points()) %}
{% do run_query(points_cartola()) %}

{% endmacro %}