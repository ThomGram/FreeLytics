from datetime import datetime

from airflow.operators.python import PythonOperator  # type: ignore

from airflow import DAG  # type: ignore


def scrape_daily_data(**context):
    """Task to scrape job data with date-based filename"""
    import subprocess  # nosec

    execution_date = context["logical_date"]
    date_str = execution_date.strftime("%Y-%m-%d")
    output_file = f"/opt/airflow/data/scraped_jobs_{date_str}.csv"

    print(f"Starting scraping for {date_str}")
    print(f"Output will be saved to: {output_file}")

    result = subprocess.run(  # nosec
        ["/opt/airflow/.venv/bin/scrapy", "crawl", "freework", "-o", output_file],
        cwd="/opt/airflow/src/scrapy_freework",
        text=True,
    )

    if result.returncode != 0:
        print(f"Scraping failed with return code: {result.returncode}")
        raise Exception(f"Scraping failed with return code: {result.returncode}")

    print(f"Scraping completed successfully for {date_str}")
    print(f"Output file: {output_file}")

    return output_file


def insert_into_datalake(**context):
    """Task to insert daily jobs scraping to datalake"""
    import os
    from dotenv import load_dotenv
    from src.datalake.create_insert import insert_into_ducklake

    load_dotenv()

    scraped_file = context["task_instance"].xcom_pull(task_ids="scrape_daily_data")

    DATALAKE_PATH = os.getenv("DATALAKE_PATH")
    TABLE_NAME = os.getenv("DUCKLAKE_TABLE_NAME")
    print(f"Using datalake path: {DATALAKE_PATH}")
    print(f"Using CSV file: {scraped_file}")
    insert_into_ducklake(
        ducklake_path=DATALAKE_PATH, csv_file=scraped_file, table_name=TABLE_NAME
    )


def cleanup_old_files(**context):
    """Task to clean up old scraped files (keep last 7 days)"""
    from datetime import timedelta
    from pathlib import Path

    execution_date = context["logical_date"]
    cutoff_date = (execution_date - timedelta(days=7)).replace(tzinfo=None)

    data_dir = Path("/opt/airflow/data")
    cleaned_files = []

    # Find old CSV files
    for csv_file in data_dir.glob("scraped_jobs_*.csv"):
        try:
            # Extract date from filename - skip files with invalid names
            filename = csv_file.name
            if not filename.startswith("scraped_jobs_") or not filename.endswith(
                ".csv"
            ):
                continue

            date_part = filename.replace("scraped_jobs_", "").replace(".csv", "")
            # Skip files with extra text (like "copy")
            if not date_part.count("-") == 2:
                print(f"Skipping file with invalid date format: {csv_file}")
                continue

            file_date = datetime.strptime(date_part, "%Y-%m-%d")

            if file_date < cutoff_date:
                print(f"Removing old file: {csv_file}")
                csv_file.unlink()
                cleaned_files.append(str(csv_file))

        except (ValueError, Exception) as e:
            print(f"Could not process file {csv_file}: {e}")

    print(f"Cleaned up {len(cleaned_files)} old files")
    return cleaned_files


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

scrape_task >> datalake_insert_task >> cleanup_task
