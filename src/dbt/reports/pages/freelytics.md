---
title: FreeLytics Dashboard
---

# FreeLytics Dashboard

<Tabs>
    <Tab label="General">

## Vue Generale par Categorie et Mois

<Dropdown name=time_range>
    <DropdownOption value=3 valueLabel="3 derniers mois"/>
    <DropdownOption value=6 valueLabel="6 derniers mois"/>
    <DropdownOption value=12 valueLabel="12 derniers mois"/>
</Dropdown>

```sql general_stats
select
    dim_job_category,
    month,
    total_jobs,
    mean_daily_rate_min,
    mean_daily_rate_max,
    mean_salary_min,
    mean_salary_max,
    pct_full_remote,
    pct_hybrid,
    pct_on_site
from freelytics_warehouse.mart_monthly_by_job_cat
where month >= current_date - interval '${inputs.time_range.value}' month
order by month desc, total_jobs desc
```

### Nombre d'annonces par rôle

<LineChart
    data={general_stats}
    title="Evolution du nombre d'annonces par rôle"
    x=month
    y=total_jobs
    series=dim_job_category
/>

### TJM Min et Max moyen par rôle

<LineChart
    data={general_stats}
    title="TJM Min moyen par rôle"
    x=month
    y=mean_daily_rate_min
    series=dim_job_category
    yAxisTitle="TJM Min moyen (EUR)"
/>

<LineChart
    data={general_stats}
    title="TJM Max moyen par rôle"
    x=month
    y=mean_daily_rate_max
    series=dim_job_category
    yAxisTitle="TJM Max moyen (EUR)"
/>

### Salaire Min et Max moyen par rôle

<LineChart
    data={general_stats}
    title="Salaire Min moyen par rôle"
    x=month
    y=mean_salary_min
    series=dim_job_category
    yAxisTitle="Salaire Min moyen (EUR)"
/>

<LineChart
    data={general_stats}
    title="Salaire Max moyen par rôle"
    x=month
    y=mean_salary_max
    series=dim_job_category
    yAxisTitle="Salaire Max moyen (EUR)"
/>

### Part d'offres Full Remote par rôle

```sql remote_by_cat
select
    dim_job_category,
    month,
    pct_full_remote/100 as "Full Remote",
from freelytics_warehouse.mart_monthly_by_job_cat
where month >= current_date - interval '${inputs.time_range.value}' month
order by month desc
```

<BarChart
    data={remote_by_cat}
    title="Distribution Full Remote par rôle"
    x=month
    y={["Full Remote"]}
    series=dim_job_category
    type=grouped
    yFmt=pct
/>

    </Tab>

    <Tab label="Cloud">

## Analyse Cloud Providers

```sql cloud_stats
select
    cloud_provider,
    month,
    skill_occurence as total_jobs,
    mean_daily_rate_min,
    mean_daily_rate_max,
    mean_salary_min,
    mean_salary_max
from freelytics_warehouse.mart_cloud_providers
where month >= current_date - interval '${inputs.time_range.value}' month
order by month desc, skill_occurence desc
```

### Nombre d'annonces Cloud

<LineChart
    data={cloud_stats}
    title="Evolution des annonces par Cloud Provider"
    x=month
    y=total_jobs
    series=cloud_provider
/>

### TJM Cloud Providers

<LineChart
    data={cloud_stats}
    title="TJM Min moyen par Cloud Provider"
    x=month
    y=mean_daily_rate_min
    series=cloud_provider
    yAxisTitle="TJM Min (EUR)"
/>

<LineChart
    data={cloud_stats}
    title="TJM Max moyen par Cloud Provider"
    x=month
    y=mean_daily_rate_max
    series=cloud_provider
    yAxisTitle="TJM Max (EUR)"
/>

### Salaire Cloud Providers

<LineChart
    data={cloud_stats}
    title="Salaire Min moyen par Cloud Provider"
    x=month
    y=mean_salary_min
    series=cloud_provider
    yAxisTitle="Salaire Min (EUR)"
/>

<LineChart
    data={cloud_stats}
    title="Salaire Max moyen par Cloud Provider"
    x=month
    y=mean_salary_max
    series=cloud_provider
    yAxisTitle="Salaire Max (EUR)"
/>

    </Tab>

    <Tab label="DE/DS/AE">

## Data Engineering, Data Science, Analytics Engineering

<Dropdown name=job_category>
    <DropdownOption value="data engineer" valueLabel="Data Engineering"/>
    <DropdownOption value="data scientist" valueLabel="Data Science"/>
    <DropdownOption value="analytics engineer" valueLabel="Analytics Engineering"/>
</Dropdown>

```sql data_jobs
select
    month,
    total_jobs,
    mean_daily_rate_min,
    mean_daily_rate_max,
    mean_salary_min,
    mean_salary_max,
    pct_full_remote/100 as pct_full_remote,
    pct_hybrid/100 as pct_hybrid,
    pct_on_site/100 as pct_on_site,
    pct_junior/100 as pct_junior,
    pct_confirme/100 as pct_confirme,
    pct_senior/100 as pct_senior,
    pct_expert/100 as pct_expert,
    mean_duration,
    pct_open_to_freelance/100 as pct_open_to_freelance,
    pct_open_to_cdi/100 as pct_open_to_cdi,
    pct_open_to_cdd/100 as pct_open_to_cdd
from freelytics_warehouse.mart_monthly_by_job_cat
where dim_job_category = '${inputs.job_category.value}'
    and month >= current_date - interval '${inputs.time_range.value}' month
order by month desc
```

### TJM et Salaire

<LineChart
    data={data_jobs}
    title="Evolution TJM pour ${inputs.job_category.value}"
    x=month
    y={["mean_daily_rate_min", "mean_daily_rate_max"]}
    yAxisTitle="TJM (EUR)"
/>

<LineChart
    data={data_jobs}
    title="Evolution Salaire pour ${inputs.job_category.value}"
    x=month
    y={["mean_salary_min", "mean_salary_max"]}
    yAxisTitle="Salaire (EUR)"
/>

### Remote

<BarChart
    data={data_jobs}
    title="Distribution Remote pour ${inputs.job_category.value}"
    x=month
    y={["pct_full_remote", "pct_hybrid", "pct_on_site"]}
    yFmt=pct
/>

### Seniorite

<BarChart
    data={data_jobs}
    title="Distribution par Seniorite pour ${inputs.job_category.value}"
    x=month
    y={["pct_junior", "pct_confirme", "pct_senior", "pct_expert"]}
    yFmt=pct
/>

### Duree Moyenne

<LineChart
    data={data_jobs}
    title="Duree moyenne des missions pour ${inputs.job_category.value}"
    x=month
    y=mean_duration
    yAxisTitle="Duree (mois)"
/>

### Type de Contrat

<BarChart
    data={data_jobs}
    title="Distribution par Type de Contrat pour ${inputs.job_category.value}"
    x=month
    y={["pct_open_to_freelance", "pct_open_to_cdi", "pct_open_to_cdd"]}
    yFmt=pct
/>

    </Tab>

    <Tab label="Skills">

## Top Skills

### Top 10 Skills (All Time)

```sql top_skills_all_time
select
    skill,
    sum(skill_occurence) as total_occurences
from freelytics_warehouse.mart_skills_by_job_cat_by_month
group by skill
order by total_occurences desc
limit 10
```

<BarChart
    data={top_skills_all_time}
    title="Top 10 Skills All Time"
    x=skill
    y=total_occurences
    swapXY=true
/>

### Top 10 Skills (Mois précédent)

```sql top_skills_current_month
select
    skill,
    sum(skill_occurence) as total_occurences
from freelytics_warehouse.mart_skills_by_job_cat_by_month
where month = date_trunc('month', current_date - interval '1 month')
group by skill
order by total_occurences desc
limit 10
```

<BarChart
    data={top_skills_current_month}
    title="Top 10 Skills mois précédent"
    x=skill
    y=total_occurences
    swapXY=true
/>


## Top Skills par rôle


<Dropdown name=job_category>
    <DropdownOption value="data engineer" valueLabel="Data Engineering"/>
    <DropdownOption value="data scientist" valueLabel="Data Science"/>
    <DropdownOption value="analytics engineer" valueLabel="Analytics Engineering"/>
</Dropdown>

### Top 10 Skills (All Time)

```sql top_skills_all_time
select
    skill,
    sum(skill_occurence) as total_occurences
from freelytics_warehouse.mart_skills_by_job_cat_by_month
where dim_job_category = '${inputs.job_category.value}'

group by skill, '${inputs.job_category.value}'
order by total_occurences desc
limit 10
```

<BarChart
    data={top_skills_all_time}
    title="Top 10 Skills All Time"
    x=skill
    y=total_occurences
    swapXY=true
/>

### Top 10 Skills (Mois précédent)

```sql top_skills_current_month
select
    skill,
    sum(skill_occurence) as total_occurences
from freelytics_warehouse.mart_skills_by_job_cat_by_month
where month = date_trunc('month', current_date - interval '1 month') and  dim_job_category = '${inputs.job_category.value}'
group by skill, '${inputs.job_category.value}'
order by total_occurences desc
limit 10
```

<BarChart
    data={top_skills_current_month}
    title="Top 10 Skills mois précédent"
    x=skill
    y=total_occurences
    swapXY=true
/>
    </Tab>

    <Tab label="Companies">

## Analyse par Entreprise

```sql company_stats
select
    dim_company_name,
    sum(total_jobs) as total_jobs,
    avg(mean_daily_rate_max) as avg_tjm,
    avg(mean_salary_max) as avg_salary,
    avg(pct_open_to_freelance)/100 as prop_freelance,
    avg(pct_open_to_cdi)/100 as prop_cdi,
    avg(pct_full_remote)/100 as pct_remote
from freelytics_warehouse.mart_monthly_by_company
where month >= current_date - interval '${inputs.time_range.value}' month
group by dim_company_name
having sum(total_jobs) >= 3
order by total_jobs desc
limit 20
```

### Top 20 Entreprises par nombre d'annonces

<DataTable data={company_stats} rows=20>
    <Column id=dim_company_name title="Entreprise"/>
    <Column id=total_jobs title="Nb Annonces" fmt=num0/>
    <Column id=avg_tjm title="TJM Moyen" fmt=eur/>
    <Column id=avg_salary title="Salaire Moyen" fmt=eur/>
    <Column id=prop_freelance title="% Freelance" fmt=pct/>
    <Column id=prop_cdi title="% CDI" fmt=pct/>
    <Column id=pct_remote title="% Remote" fmt=pct/>
</DataTable>

### TJM Moyen par Entreprise

<BarChart
    data={company_stats}
    title="TJM Moyen par Entreprise (Top 20)"
    x=dim_company_name
    y=avg_tjm
    swapXY=true
    yAxisTitle="TJM Moyen (EUR)"
/>

### Distribution Remote par Entreprise

<BarChart
    data={company_stats}
    title="Pourcentage Remote par Entreprise (Top 20)"
    x=dim_company_name
    y=pct_remote
    swapXY=true
    yFmt=pct
/>

    </Tab>
</Tabs>
