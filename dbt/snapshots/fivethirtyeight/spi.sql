{% snapshot spi_snapshot %}

{{
    config(
      target_schema="fivethirtyeight",
      unique_key="season||'-'||league_id||'-'||team1||'-'||team2",
      strategy="timestamp",
      updated_at="loaded_at",
    )
}}

SELECT * FROM {{ source("fivethirtyeight", "spi") }}

{% endsnapshot %}