{{ config(materialized='table') }}

with ranked as (
  select *,
    row_number() over (
      partition by job_url
      order by
        coalesce(inserted_at, updated_at) desc
    ) as rn
  from {{ source('lake_raw', 'freelytics_raw') }}
)
select * exclude(rn)
from ranked
where rn = 1
