with cleaned_start_date as
    (
        select * from {{ref("int_job_listings_clean_start_date")}}
    ),

    normalized_duration as
    (
        select job_url,
             case
                when duration like '%jour%' then
                    cast(regexp_extract(duration, '[0-9]+') as int) / 30.0
                when duration like '%mois%' then
                    cast(regexp_extract(duration, '[0-9]+') as int)
                when duration like '%an%' then
                    cast(regexp_extract(duration, '[0-9]+') as int) * 12
                else null
             end as duration_months
        from cleaned_start_date
    )

select csd.* exclude(duration),
       nd.duration_months as duration,
    from cleaned_start_date csd left join normalized_duration nd on csd.job_url = nd.job_url
