{% snapshot dim_player_last_snapshot %}

{{
    config(
      target_schema="palpiteiro",
      unique_key="id",
      strategy="timestamp",
      updated_at="materialized_at",
    )
}}

select * from {{ ref("dim_player_last") }}

{% endsnapshot %}