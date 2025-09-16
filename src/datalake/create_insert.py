import os
import duckdb
from pathlib import Path
from dotenv import load_dotenv
from string import Template
from src.datalake.utils import template_to_query_substitution


DATEQUERY = """
with split_str as
    (select *,
        case
            when '-' in publication_date
                then left(publication_date, instr(publication_date, '-')-2)
                else publication_date end as published_at_str,
        case
            when '-' in publication_date
                then right(publication_date, instr(publication_date, '-'))
                else null end as updated_at_str
        from read_csv('$path'))
select *,
        strptime(right(published_at_str, 10), '%d/%m/%Y')  as published_at,
        case
            when updated_at_str is not null
                then strptime(right(updated_at_str, 10), '%d/%m/%Y')
                else strptime(right(published_at_str, 10), '%d/%m/%Y') end as updated_at
        from split_str;


"""


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
    query = template_to_query_substitution(
        f"ATTACH 'ducklake:{ducklake_path}' AS freelytics_ducklake;",
        {"ducklake_path": ducklake_path},
    )
    duckdb.sql(query)
    duckdb.sql("USE freelytics_ducklake;")

    substitution_dict = {"table": table_name, "path": csv_file}

    if mode == "create_or_replace":
        query = template_to_query_substitution(
            f"CREATE OR REPLACE TABLE $table AS {DATEQUERY};", substitution_dict
        )
        duckdb.sql(query)
        print(f"Created/replaced table '{table_name}'")

    elif mode == "append":
        try:
            template = Template(f"CREATE TABLE $table AS  {DATEQUERY};")
            query = template_to_query_substitution(
                f"CREATE TABLE $table AS  {DATEQUERY};", substitution_dict
            )
            duckdb.sql(query)
            print(f"Created new table '{table_name}'")
        except (duckdb.CatalogException, duckdb.Error):
            template = f"INSERT INTO $table  {DATEQUERY};"
            query = template_to_query_substitution(template, substitution_dict)
            print(query)
            duckdb.sql(query)
            print(f"Appended to existing table '{table_name}'")

    elif mode == "create_only":
        template = f"CREATE TABLE $table AS  {DATEQUERY};"
        query = template_to_query_substitution(template, substitution_dict)
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
