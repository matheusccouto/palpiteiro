{% macro points() %}

CREATE OR REPLACE FUNCTION palpiteiro.points(x NUMERIC) RETURNS NUMERIC
REMOTE WITH CONNECTION `us-east4.remote-function`
OPTIONS (endpoint = 'https://us-east4-palpiteiro-{{ target.name }}.cloudfunctions.net/points')

{% endmacro %}