import duckdb
from src.datalake.utils import template_to_query_substitution


def add_date_columns_to_existing_table(ducklake_path, table_name):
    """
    Add date parsing columns to an existing table
    """
    conn = duckdb.connect()

    try:
        # Connect to ducklake
        conn.sql("INSTALL ducklake;")
        conn.sql("LOAD ducklake;")
        lake_attach_template = (
            f"ATTACH 'ducklake:{ducklake_path}' AS freelytics_ducklake;"
        )
        query = template_to_query_substitution(
            lake_attach_template, {"ducklake_path": ducklake_path}
        )
        conn.sql(query)
        conn.sql("USE freelytics_ducklake;")

        # Check if table exists
        template = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '$table_name';"
        query = template_to_query_substitution(template, {"table_name": table_name})
        result = conn.sql(query).fetchone()
        if result[0] == 0:
            raise ValueError(f"Table '{table_name}' does not exist")

        print(f"Modifying existing table '{table_name}'...")

        # Start transaction for safety
        conn.sql("BEGIN TRANSACTION;")

        try:
            # Add new columns (if they don't exist)
            columns_to_add = [
                "published_at_str TEXT",
                "updated_at_str TEXT",
                "published_at DATE",
                "updated_at DATE",
            ]

            for column_def in columns_to_add:
                try:
                    add_column_template = (
                        f"ALTER TABLE {table_name} ADD COLUMN {column_def};"
                    )
                    add_column_query = template_to_query_substitution(
                        add_column_template,
                        {"table_name": table_name, "column_def": column_def},
                    )
                    conn.sql(add_column_query)
                    print(f"Added column: {column_def}")
                except duckdb.CatalogException:
                    print(f"Column already exists: {column_def.split()[0]}")

            # Populate string columns
            update_str_query = """
            UPDATE $table_name
            SET
                published_at_str = CASE
                    WHEN '-' IN publication_date
                    THEN LEFT(publication_date, INSTR(publication_date, '-') - 2)
                    ELSE publication_date
                END,
                updated_at_str = CASE
                    WHEN '-' IN publication_date
                    THEN SUBSTRING(publication_date, INSTR(publication_date, '-'))
                    ELSE NULL
                END
            WHERE published_at_str IS NULL OR updated_at_str IS NULL;
            """
            query = template_to_query_substitution(
                update_str_query, {"table_name": table_name}
            )
            conn.sql(query)
            print("Updated string columns")

            # Populate date columns
            update_date_query = """
            UPDATE $table_name
            SET
                published_at = (strptime(RIGHT(published_at_str, 10), '%d/%m/%Y')),
                updated_at = CASE
                    WHEN updated_at_str IS NOT NULL AND updated_at_str != ''
                    THEN (strptime(RIGHT(updated_at_str, 10), '%d/%m/%Y'))
                    ELSE (strptime(RIGHT(updated_at_str, 10), '%d/%m/%Y'))
                END
            WHERE published_at IS NULL;
            """
            query = template_to_query_substitution(
                update_date_query, {"table_name": table_name}
            )
            conn.sql(query)
            print("Updated date columns")

            # Commit transaction
            conn.sql("COMMIT;")
            print(f"Successfully modified table '{table_name}'")

        except Exception as e:
            # Rollback on error
            conn.sql("ROLLBACK;")
            print(f"Error occurred, rolling back: {e}")
            raise

    except Exception as e:
        print(f"Error modifying table: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    DATALAKE_PATH = os.getenv("DATALAKE_PATH")
    TABLE_NAME = os.getenv("DUCKLAKE_TABLE_NAME")

    add_date_columns_to_existing_table(DATALAKE_PATH, TABLE_NAME)
