with job_listings_cleaned_revenue as
    (select * from {{ ref('int_job_listings_split_revenu')}}),

    cleaned_start_date as
    (select job_url,
        case when start_date like('%Dès que possible%')
                then true
                else false
        end as ASAP_start,
        case when start_date not like('%Dès que possible%') and start_date is not null and trim(start_date) != ''
                then cast(strptime(start_date, '%d/%m/%Y') as date)
                else null
            end as start_date_as_date
        from job_listings_cleaned_revenue)

select jl_cleand.* exclude(start_date),
       csd.ASAP_start,
       csd.start_date_as_date as start_date
    from job_listings_cleaned_revenue jl_cleand left join cleaned_start_date csd on jl_cleand.job_url = csd.job_url
