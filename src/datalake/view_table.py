import os
import duckdb
from dotenv import load_dotenv
from src.datalake.utils import template_to_query_substitution


def view_table():
    load_dotenv()

    DATALAKE_PATH = os.getenv("DATALAKE_PATH")
    TABLE_NAME = os.getenv("DUCKLAKE_TABLE_NAME")

    conn = duckdb.connect()

    # Connect to ducklake
    conn.sql("INSTALL ducklake;")
    conn.sql("LOAD ducklake;")
    conn.sql(f"ATTACH 'ducklake:{DATALAKE_PATH}' AS freelytics_ducklake;")
    conn.sql("USE freelytics_ducklake;")

    # Get data
    template = "SELECT * FROM $table_name where updated_at_str is not null"
    query = template_to_query_substitution(template, {"table_name": TABLE_NAME})
    df = conn.sql(query).df()

    # Print info
    print(f"Table: {TABLE_NAME}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nData:")
    print(df.head())

    conn.close()


if __name__ == "__main__":
    view_table()
