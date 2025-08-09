import sys
from datetime import datetime

from airflow.operators.python import PythonOperator  # type: ignore

from airflow import DAG  # type: ignore

sys.path.insert(0, "/opt/airflow/src")


def scrape_daily_data(**context):
    """Task to scrape job data with date-based filename"""
    import subprocess  # nosec

    execution_date = context["execution_date"]
    date_str = execution_date.strftime("%Y-%m-%d")
    output_file = f"/opt/airflow/data/scraped_jobs_{date_str}.csv"

    result = subprocess.run(  # nosec
        ["/opt/airflow/.venv/bin/scrapy", "crawl", "freework", "-o", output_file],
        cwd="/opt/airflow/src/scrapy_freework",
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(f"Scraping failed: {result.stderr}")

    print(f"Scraping completed for {date_str}: {result.stdout}")
    print(f"Output file: {output_file}")

    return output_file


default_args = {
    "owner": "freelytics",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
}

dag = DAG(
    "daily_scraping_pipeline",
    default_args=default_args,
    description="Daily FreeLytics scraping pipeline",
    schedule_interval="@daily",
    catchup=False,
    tags=["daily", "scraping"],
)

scrape_task = PythonOperator(
    task_id="scrape_daily_data",
    python_callable=scrape_daily_data,
    dag=dag,
)
