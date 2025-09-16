{{ config(materialized='table') }}

select * from {{ ref('stg_raw_job_listings_incr')}} where dbt_valid_to = DATE '9999-12-31'
