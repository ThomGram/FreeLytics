import os
import duckdb
from pathlib import Path
from dotenv import load_dotenv
from string import Template


def insert_into_ducklake(ducklake_path, csv_file, table_name, mode="append"):
    """
    mode options:
    - 'create_or_replace': Replace table if exists, create if not
    - 'append': Add to existing table, create if not exists
    - 'create_only': Only create if table doesn't exist, raise error if exists
    """
    ducklake_dir = Path(ducklake_path).parent
    if not Path(ducklake_dir).exists():
        Path(ducklake_dir).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {ducklake_dir}")

    if not Path(csv_file).exists():
        raise FileNotFoundError(f"CSV file does not exist: {csv_file}")

    duckdb.sql("INSTALL ducklake;")
    duckdb.sql("LOAD ducklake;")
    duckdb.sql(f"ATTACH 'ducklake:{ducklake_path}' AS freelytics_ducklake;")
    duckdb.sql("USE freelytics_ducklake;")

    if mode == "create_or_replace":
        template = Template(
            "CREATE OR REPLACE TABLE $table AS SELECT * FROM read_csv('$path');"
        )
        query = template.substitute(table=(table_name), path=(csv_file))
        duckdb.sql(query)
        print(f"Created/replaced table '{table_name}'")

    elif mode == "append":
        try:
            template = Template(
                "CREATE TABLE $table AS SELECT * FROM read_csv('$path');"
            )
            query = template.substitute(table=(table_name), path=(csv_file))
            duckdb.sql(query)
            print(f"Created new table '{table_name}'")
        except (duckdb.CatalogException, duckdb.Error):
            template = Template("INSERT INTO $table SELECT * FROM read_csv('$path');")
            query = template.substitute(table=(table_name), path=(csv_file))
            print(query)
            duckdb.sql(query)
            print(f"Appended to existing table '{table_name}'")

    elif mode == "create_only":
        template = Template("CREATE TABLE $table AS SELECT * FROM read_csv('$path');")
        query = template.substitute(table=(table_name), path=(csv_file))
        duckdb.sql(query)
        print(f"Created new table '{table_name}'")


def main():
    load_dotenv()
    DATALAKE_PATH = os.getenv("DATALAKE_PATH")
    CSV_TEST_FILE = os.getenv("CSV_TEST_FILE")
    TABLE_NAME = os.getenv("DUCKLAKE_TABLE_NAME")
    print(f"Using datalake path: {DATALAKE_PATH}")
    print(f"Using CSV file: {CSV_TEST_FILE}")
    insert_into_ducklake(
        ducklake_path=DATALAKE_PATH, csv_file=CSV_TEST_FILE, table_name=TABLE_NAME
    )


if __name__ == "__main__":
    main()
