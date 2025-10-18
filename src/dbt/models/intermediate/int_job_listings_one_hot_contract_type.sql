select * exclude(contract_types, remote_work),
    coalesce(contract_types like '%Freelance%', false) as is_open_to_freelance,
    coalesce(contract_types like '%CDI%', false) as is_open_to_cdi,
    coalesce(contract_types like '%CDD%', false) as is_open_to_cdd,
    coalesce(remote_work like '%100%', false) as is_fully_remote,
    coalesce(remote_work like '%partiel%', false) as is_partially_remote,
    remote_work is null as is_not_remote
from {{ ref('int_job_listings_normalized_location') }}
