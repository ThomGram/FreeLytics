with raw_job_listings as
    (select * from {{ ref('stg_job_listings')}}),

    rm_special_characters as
    (select job_url,
            case
                when salary not null
                  then  trim(split_part(salary, '€', 1))
                else null end as salary_no_spe_charac,
            case
                when daily_rate not null
                  then  trim(split_part(daily_rate, '€', 1))
                else null  end  as daily_rate_no_spe_charac
            from raw_job_listings),

    split_salary_daily_rate_min_max_str as
    (select *,
            {{revenu_to_min_max_str("salary_no_spe_charac", "min")}} as salary_min_str,
            {{revenu_to_min_max_str("salary_no_spe_charac", "max")}} as salary_max_str,
            {{revenu_to_min_max_str("daily_rate_no_spe_charac", "min")}} as daily_rate_min_str,
            {{revenu_to_min_max_str("daily_rate_no_spe_charac", "max")}} as daily_rate_max_str
            from  rm_special_characters),

    job_listings_with_min_max_salary_and_daily_rate as
    (select *,
            {{revenu_to_int("salary_min_str")}} as salary_min,
            {{revenu_to_int("salary_max_str")}} as salary_max,
            {{revenu_to_int("daily_rate_min_str")}} as daily_rate_min,
            {{revenu_to_int("daily_rate_max_str")}} as daily_rate_max
            from split_salary_daily_rate_min_max_str)

select raw_job.*,
        minmax.salary_min,
        minmax.salary_max,
        minmax.daily_rate_min,
        minmax.daily_rate_max

        from {{ ref('stg_job_listings')}} raw_job
            left join job_listings_with_min_max_salary_and_daily_rate minmax
                on raw_job.job_url = minmax.job_url
