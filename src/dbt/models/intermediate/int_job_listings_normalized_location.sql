with

normalized_duration as(
    select * from {{ ref('int_job_listings_normalized_duration') }}
),

parsed_location as (
    select location, job_url,
        length(location) - length(replace(location, ',', '')) as nb_commas,
        array_length(string_to_array(location, ','), 1) as nb_elements
    from {{ ref('int_job_listings_normalized_duration') }}
),

adaptive_parsing as (
    select
        job_url, location,
        nb_elements,

        case
            when nb_elements = 1 then
                array[null, null, null, trim(location)]
            when nb_elements = 3 then
                array[trim(split_part(location, ',', 1)), trim(split_part(location, ',', 2)), trim(split_part(location, ',', 3))]
            when nb_elements = 2 then
                array[null, trim(split_part(location, ',', 1)), trim(split_part(location, ',', 2))]
            else
                array[null, null, location]
        end as parsed_array

    from parsed_location
),

structured_data as (
    select
        job_url,
        nb_elements,
        trim(parsed_array[1]) as code_postal,
        trim(parsed_array[2]) as ville,
        trim(parsed_array[3]) as region,
    from adaptive_parsing
),

cleaned_structured_data as (
    select
        job_url,
        nb_elements,
        code_postal,
        case
            when structured_data.ville like '%Île-de-France%' then ''
            else structured_data.ville
        end as ville,
        case
            when structured_data.ville like '%Île-de-France%' then structured_data.ville
            when structured_data.ville like '%Paris%' then 'Île-de-France'
            else structured_data.region
        end as region

    from structured_data
)

select nd.* ,
       sd.code_postal,
       sd.ville,
       sd.region,
    from normalized_duration nd left join cleaned_structured_data sd on nd.job_url = sd.job_url
