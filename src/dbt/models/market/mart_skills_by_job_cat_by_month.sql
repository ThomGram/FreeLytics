WITH skills_data AS (
  SELECT
    dim_job_category,
    dim_published_at,
    unnest(dim_skills_array) as skill
  FROM {{ref('mart_job_listings')}}
)
select dim_job_category, skill, count(skill) as skill_occurence, date_trunc('month', dim_published_at) as month
from skills_data where dim_job_category not in lower(skill)
GROUP BY dim_job_category, date_trunc('month', dim_published_at), skill
ORDER BY date_trunc('month', dim_published_at) DESC, dim_job_category
