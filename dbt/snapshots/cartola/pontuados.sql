{% snapshot pontuados_snapshot %}

{{
    config(
      target_schema="cartola",
      unique_key="temporada||'-'||rodada||'-'||id",
      strategy="timestamp",
      updated_at="loaded_at",
    )
}}

SELECT * FROM {{ source("cartola", "pontuados") }}

{% endsnapshot %}