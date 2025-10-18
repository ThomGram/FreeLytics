from datetime import datetime
import os
from dotenv import load_dotenv

from airflow.operators.bash import BashOperator  # type: ignore
from airflow import DAG  # type: ignore

# Load environment variables
load_dotenv("/opt/airflow/.env")

# Environment variables for dbt tasks
DBT_ENV = {
    "DATABASE_PATH": os.getenv("DATABASE_PATH"),
    "DATALAKE_PATH": os.getenv("DATALAKE_PATH"),
    "HOME": os.getenv("HOME", "/opt/airflow"),
}

default_args = {
    "owner": "freelytics",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}

dag = DAG(
    "dbt_pipeline",
    default_args=default_args,
    description="dbt data transformations (dedup, snapshot, models)",
    schedule=None,  # Triggered by scraping_pipeline
    catchup=False,
    tags=["dbt", "transformation", "warehouse"],
    max_active_runs=1,
)

dbt_run_staging = BashOperator(
    task_id="dbt_run_staging",
    bash_command="cd /opt/airflow/src/dbt && /opt/airflow/.venv/bin/dbt run --select stg_raw_job_listings_deduped",
    env=DBT_ENV,
    dag=dag,
)

dbt_snapshot = BashOperator(
    task_id="dbt_snapshot",
    bash_command="cd /opt/airflow/src/dbt && /opt/airflow/.venv/bin/dbt snapshot",
    env=DBT_ENV,
    dag=dag,
)

dbt_build = BashOperator(
    task_id="dbt_build",
    bash_command="cd /opt/airflow/src/dbt && /opt/airflow/.venv/bin/dbt build --exclude stg_raw_job_listings_deduped",
    env=DBT_ENV,
    dag=dag,
)

# Pipeline flow: dedup → snapshot → build all models
dbt_run_staging >> dbt_snapshot >> dbt_build
