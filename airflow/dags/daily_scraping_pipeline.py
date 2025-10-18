from datetime import datetime

from airflow.operators.trigger_dagrun import TriggerDagRunOperator  # type: ignore
from airflow import DAG  # type: ignore


default_args = {
    "owner": "freelytics",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}

dag = DAG(
    "daily_scraping_pipeline",
    default_args=default_args,
    description="Daily FreeLytics complete pipeline: scraping + dbt",
    schedule="@daily",
    catchup=False,
    tags=["daily", "orchestration"],
    max_active_runs=1,
)

# Trigger scraping pipeline
trigger_scraping = TriggerDagRunOperator(
    task_id="trigger_scraping_pipeline",
    trigger_dag_id="scraping_pipeline",
    wait_for_completion=True,
    dag=dag,
)

# Trigger dbt pipeline after scraping completes
trigger_dbt = TriggerDagRunOperator(
    task_id="trigger_dbt_pipeline",
    trigger_dag_id="dbt_pipeline",
    wait_for_completion=True,
    dag=dag,
)

# Pipeline flow: scraping → dbt
trigger_scraping >> trigger_dbt
