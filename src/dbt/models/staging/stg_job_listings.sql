{{ config(materialized='table') }}

select * from {{ ref('job_listings_snapshot')}} where dbt_valid_to = DATE '9999-12-31'
