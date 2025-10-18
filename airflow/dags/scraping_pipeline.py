from datetime import datetime

from airflow.operators.python import PythonOperator  # type: ignore
from airflow import DAG  # type: ignore

from utils import scrape_daily_data, insert_into_datalake, cleanup_old_files


default_args = {
    "owner": "freelytics",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}

dag = DAG(
    "scraping_pipeline",
    default_args=default_args,
    description="Daily web scraping and data lake insertion",
    schedule="@daily",
    catchup=False,
    tags=["daily", "scraping", "datalake"],
    max_active_runs=1,
)

scrape_task = PythonOperator(
    task_id="scrape_daily_data",
    python_callable=scrape_daily_data,
    dag=dag,
)

datalake_insert_task = PythonOperator(
    task_id="insert_to_datalake",
    python_callable=insert_into_datalake,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id="cleanup_old_files",
    python_callable=cleanup_old_files,
    dag=dag,
)

# Pipeline flow: scrape → insert → cleanup
scrape_task >> datalake_insert_task >> cleanup_task
