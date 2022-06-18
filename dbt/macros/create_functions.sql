{% macro create_udfs() %}

{% do run_query(points()) %}

{% endmacro %}