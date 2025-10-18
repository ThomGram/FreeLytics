with source as (
    select *
    from {{ref("mart_job_listings")}}
)

select

    dim_job_category,
    date_trunc('month', dim_published_at) as month,

    SUM(CASE WHEN dim_experience LIKE '%< 2%' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as pct_junior,
    SUM(CASE WHEN dim_experience LIKE '%2 à 5%' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as pct_confirme,
    SUM(CASE WHEN dim_experience LIKE '%5 à 10%' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as pct_senior,
    SUM(CASE WHEN dim_experience LIKE '%> 10%' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as pct_expert,

    count(*) as total_jobs,

    100 * sum(case when dim_is_open_to_freelance is true then 1 else 0 end)/count(*) as pct_open_to_freelance,
    100 * sum(case when dim_is_open_to_cdi is true then 1 else 0 end)/count(*) as pct_open_to_cdi,
    100 * sum(case when dim_is_open_to_cdd is true then 1 else 0 end)/count(*) as pct_open_to_cdd,

    100 * sum(case when dim_is_fully_remote is true then 1 else 0 end)/count(*) as pct_full_remote,
    100 * sum(case when dim_is_partially_remote is true then 1 else 0 end)/count(*) as pct_hybrid,
    100 * sum(case when dim_is_not_remote is true then 1 else 0 end)/count(*) as pct_on_site,

    avg(fact_salary_min) as mean_salary_min,
    avg(fact_salary_max) as mean_salary_max,
    quantile_cont(fact_salary_min, [0.0, 0.25, 0.5, 0.75, 1.0]) as salary_min_quantiles,
    quantile_cont(fact_salary_max, [0.0, 0.25, 0.5, 0.75, 1.0]) as salary_max_quantiles,

    avg(fact_daily_rate_min) as mean_daily_rate_min,
    avg(fact_daily_rate_max) as mean_daily_rate_max,
    quantile_cont(fact_daily_rate_max, [0.0, 0.25, 0.5, 0.75, 1.0]) as tjm_max_quantiles,
    quantile_cont(fact_daily_rate_min, [0.0, 0.25, 0.5, 0.75, 1.0]) as tjm_min_quantiles,



    avg(fact_duration) as mean_duration,
    quantile_cont(fact_duration, [0.0, 0.25, 0.5, 0.75, 1.0]) as duration_quantiles,

from source
group by dim_job_category, date_trunc('month', dim_published_at)
