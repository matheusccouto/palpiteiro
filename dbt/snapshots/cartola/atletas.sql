{% snapshot atletas_snapshot %}

{{
    config(
      target_schema="cartola",
      unique_key="temporada_id||'-'||rodada_id||'-'||atleta_id",
      strategy="timestamp",
      updated_at="loaded_at",
    )
}}

SELECT * FROM {{ source("cartola", "atletas") }}

{% endsnapshot %}