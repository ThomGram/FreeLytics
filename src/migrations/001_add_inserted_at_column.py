"""
Migration: Add inserted_at column to freelytics_raw table

Date: 2025-10-18
Description: Adds inserted_at TIMESTAMP column to track when data was inserted into the data lake
"""

import os
import duckdb
from pathlib import Path
from dotenv import load_dotenv


def migrate_up(datalake_path: str):
    """Apply the migration - add inserted_at column"""
    print(f"Applying migration to: {datalake_path}")

    # Check if database exists
    if not Path(datalake_path).exists():
        raise FileNotFoundError(f"Database not found at: {datalake_path}")

    try:
        # Connect using DuckLake
        duckdb.sql("INSTALL ducklake;")
        duckdb.sql("LOAD ducklake;")
        duckdb.sql(f"ATTACH 'ducklake:{datalake_path}' AS db;")
        duckdb.sql("USE db;")

        # Check if column already exists
        columns = duckdb.sql("PRAGMA table_info(freelytics_raw)").fetchall()
        column_names = [col[1] for col in columns]

        if "inserted_at" in column_names:
            print("Column 'inserted_at' already exists - skipping")
            return

        # Add the column
        print("Adding column 'inserted_at'...")
        duckdb.sql("ALTER TABLE freelytics_raw ADD COLUMN inserted_at TIMESTAMP;")

        # Verify
        result = duckdb.sql("PRAGMA table_info(freelytics_raw)").fetchall()
        if any(col[1] == "inserted_at" for col in result):
            print("Migration completed successfully")
            print(f"Table now has {len(result)} columns")
        else:
            raise Exception("Migration failed - column not added")

    except Exception as e:
        print(f"Migration failed: {e}")
        raise


def main():
    """Run the migration using environment variables"""
    load_dotenv()

    datalake_path = os.getenv("DATALAKE_PATH")
    if not datalake_path:
        raise ValueError("DATALAKE_PATH environment variable not set")

    print("=" * 60)
    print("Migration: Add inserted_at column")
    print("=" * 60)

    migrate_up(datalake_path)

    print("\nMigration complete!")


if __name__ == "__main__":
    main()
