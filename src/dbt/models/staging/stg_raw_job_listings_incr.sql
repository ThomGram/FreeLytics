{{ config(
     materialized='incremental',
     unique_key='job_url',
     incremental_strategy='merge'
) }}

with base as (
  select
    *
  from {{ ref('job_listings_snapshot') }}
  {% if is_incremental() %}
    where updated_at > (select coalesce(max(updated_at), timestamp '1970-01-01') from {{ this }})
  {% endif %}
),
ranked as (
  select *,
    row_number() over (
      partition by job_url
      order by updated_at desc
    ) as rn
  from base
)
select * exclude(rn)
from ranked
where rn = 1
