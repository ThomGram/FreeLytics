from typing import List, Optional

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
