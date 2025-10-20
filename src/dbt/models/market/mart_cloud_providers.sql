{{ config(materialized='table') }}

WITH skills_data AS (
  SELECT
    dim_job_category,
    fact_daily_rate_min,
    fact_daily_rate_max,
    fact_salary_min,
    fact_salary_max,
    dim_published_at,
    unnest(dim_skills_array) as skill
  FROM {{ ref('mart_job_listings') }}
)

select
  skill as cloud_provider,
  date_trunc('month', dim_published_at) as month,

  count(skill) as skill_occurence,

  avg(fact_daily_rate_min) as mean_daily_rate_min,
  avg(fact_daily_rate_max) as mean_daily_rate_max,

  quantile_cont(fact_daily_rate_min, [0.0, 0.25, 0.5, 0.75, 1.0]) as tjm_min_quantiles,
  quantile_cont(fact_daily_rate_max, [0.0, 0.25, 0.5, 0.75, 1.0]) as tjm_max_quantiles,

  avg(fact_salary_min) as mean_salary_min,
  avg(fact_salary_max) as mean_salary_max,

  quantile_cont(fact_salary_min, [0.0, 0.25, 0.5, 0.75, 1.0]) as salary_min_quantiles,
  quantile_cont(fact_salary_max, [0.0, 0.25, 0.5, 0.75, 1.0]) as salary_max_quantiles

from skills_data
where skill in ('Azure', 'AWS Cloud', 'Google Cloud Platform (GCP)')
GROUP BY date_trunc('month', dim_published_at), skill
ORDER BY date_trunc('month', dim_published_at) DESC, skill
