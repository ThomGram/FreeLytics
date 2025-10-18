with source as (
    select *
    from {{ref("int_job_listings_one_hot_contract_type")}}
    where dbt_valid_to = CAST('9999-12-31' AS DATE)
)

select
    md5(job_url) as id,

    job_title as dim_job_title,
    job_category as dim_job_category,
    company_name as dim_company_name,
    ville as dim_ville,
    region as dim_region,
    experience as dim_experience,
    string_to_array(skills, ',') as dim_skills_array,
    published_at as dim_published_at,
    start_date as dim_start_date,

    is_open_to_freelance as dim_is_open_to_freelance,
    is_open_to_cdi as dim_is_open_to_cdi,
    is_open_to_cdd as dim_is_open_to_cdd,

    is_fully_remote as dim_is_fully_remote,
    is_partially_remote as dim_is_partially_remote,
    is_not_remote as dim_is_not_remote,

    ASAP_start as dim_ASAP_start,

    -- Facts (measures)
    salary_min as fact_salary_min,
    salary_max as fact_salary_max,
    daily_rate_min as fact_daily_rate_min,
    daily_rate_max as fact_daily_rate_max,
    duration as fact_duration,

    -- Audit fields
    updated_at

from source
