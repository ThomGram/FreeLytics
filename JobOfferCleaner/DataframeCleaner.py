import re
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger


class DataframeCleaner:

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
        ignore_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Remove duplicates from pandas DataFrame. By default considers all columns.

        Args:
            df: DataFrame to process
            ignore_columns: Optional list of column names to ignore when checking for duplicates

        Returns:
            pandas DataFrame with duplicates removed

        """
        logger.info(f"Removing duplicates from DataFrame with {len(df)} rows")

        try:
            # Handle None DataFrame
            if df is None:
                error_msg = "DataFrame is None"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Handle empty DataFrame - return as is
            if len(df) == 0:
                logger.info("DataFrame is empty, returning as is")
                return df.copy()

            # Set default ignore columns (empty list means check all columns)
            if ignore_columns is None:
                ignore_columns = []

            # Filter out non-existent columns
            ignore_columns = [col for col in ignore_columns if col in df.columns]

            # Get subset of columns to check for duplicates
            if ignore_columns:
                subset_cols = df.columns.difference(ignore_columns).tolist()
                if not subset_cols:  # All columns are ignored
                    logger.warning("All columns are ignored, returning original DataFrame")
                    return df.copy()
            else:
                subset_cols = None  # Check all columns

            result_df = df.drop_duplicates(subset=subset_cols, keep="first")
            removed_count = len(df) - len(result_df)
            logger.info(f"Removed {removed_count} duplicate rows, {len(result_df)} rows remaining")

            return result_df

        except Exception as e:
            error_msg = f"Unexpected error removing duplicates: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    @staticmethod
    def revenue_string_to_min_max(revenue: str) -> Dict[str, str]:
        """
        Convert revenue string to min/max values.

        Args:
            revenue: String like "45k €⁄an", "380-580 €⁄j", "49k-60k €⁄an"

        Returns:
            Dict with 'min' and 'max' keys containing string values
        """
        if not revenue or revenue.strip() == "":
            return {"min": "", "max": ""}

        revenue = revenue.strip()

        # Remove currency symbols and units
        clean_revenue = re.sub(r"[€⁄anjk\s]", "", revenue)

        # Handle ranges like "380-580" or "49-60"
        if "-" in clean_revenue:
            parts = clean_revenue.split("-")
            if len(parts) == 2:
                min_val = parts[0].strip()
                max_val = parts[1].strip()

                # Convert k values to full numbers
                if "k" in revenue.lower():
                    min_val = str(int(min_val) * 1000) if min_val.isdigit() else min_val
                    max_val = str(int(max_val) * 1000) if max_val.isdigit() else max_val

                return {"min": min_val, "max": max_val}

        # Handle single values like "45k" or "550"
        if clean_revenue.isdigit():
            val = clean_revenue
            # Convert k values to full numbers
            if "k" in revenue.lower():
                val = str(int(val) * 1000)
            return {"min": val, "max": val}

        # If we can't parse it, return empty
        return {"min": "", "max": ""}

    @staticmethod
    def split_revenue_to_min_max(df: pd.DataFrame) -> pd.DataFrame:
        """
        Split salary and TJM into min and max as they are expressed as a range more often than not.
        Transform to float from string with special characters and letters
        """
        logger.info("Splitting salary and TJM into their min and max")

        try:
            # Handle None DataFrame
            if df is None:
                error_msg = "DataFrame is None"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Handle empty DataFrame - return as is
            if len(df) == 0:
                logger.info("DataFrame is empty, returning as is")
                return df.copy()

            result_df = df.copy()

            # Process salary column if it exists
            if "salary" in result_df.columns:
                salary_data = result_df["salary"].apply(DataframeCleaner.revenue_string_to_min_max)
                result_df["salary_min"] = salary_data.apply(lambda x: x["min"])
                result_df["salary_max"] = salary_data.apply(lambda x: x["max"])

            # Process daily_rate column if it exists
            if "daily_rate" in result_df.columns:
                daily_rate_data = result_df["daily_rate"].apply(
                    DataframeCleaner.revenue_string_to_min_max
                )
                result_df["daily_rate_min"] = daily_rate_data.apply(lambda x: x["min"])
                result_df["daily_rate_max"] = daily_rate_data.apply(lambda x: x["max"])

            logger.info("Successfully split revenue columns into min/max")
            return result_df

        except Exception as e:
            error_msg = f"Unexpected error splitting revenue: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
