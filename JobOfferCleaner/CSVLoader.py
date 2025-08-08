import os
from typing import Optional

import pandas as pd
from loguru import logger


class CSVLoader:

    @staticmethod
    def csv_to_pandas(
        file_path: str, separator: Optional[str] = ",", encoding: str = "utf-8"
    ) -> pd.DataFrame:
        """
        Convert CSV file to pandas DataFrame with automatic separator detection

        Args:
            file_path: Path to the CSV file
            separator: Optional separator character. If None, will auto-detect
            encoding: File encoding (default: utf-8)

        Returns:
            pandas DataFrame containing the CSV data

        """
        logger.info(f"Starting CSV conversion for file: {file_path}")

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Check if file is empty
            if os.path.getsize(file_path) == 0:
                error_msg = f"File is empty: {file_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Read CSV file
            logger.debug(f"Reading CSV with pandas, separator='{separator}', encoding='{encoding}'")
            df = pd.read_csv(file_path, sep=separator, encoding=encoding)

            # Validate DataFrame
            if df.empty:
                error_msg = "CSV file resulted in empty DataFrame"
                logger.warning(error_msg)
            else:
                logger.info(
                    f"Successfully converted CSV: {len(df)} rows, {len(df.columns)} columns"
                )
                logger.debug(f"Columns: {list(df.columns)}")

            return df

        except pd.errors.EmptyDataError as e:
            error_msg = f"File is empty or contains no valid data: {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except pd.errors.ParseError as e:
            error_msg = f"Invalid CSV format: {file_path} - {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except UnicodeDecodeError as e:
            error_msg = f"Encoding error reading file: {file_path} - {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error converting CSV: {file_path} - {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
