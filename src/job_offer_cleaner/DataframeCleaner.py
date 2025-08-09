import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
from loguru import logger


class DataframeCleaner:

    @staticmethod
    def _validate_dataframe(df: pd.DataFrame, operation_name: str) -> pd.DataFrame:
        """Common validation for DataFrame inputs."""
        if df is None:
            error_msg = f"DataFrame is None for {operation_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if len(df) == 0:
            logger.info(f"DataFrame is empty for {operation_name}, returning as is")
            return df.copy()

        return df.copy()

    @staticmethod
    def _apply_column_transformation(
        df: pd.DataFrame,
        column_name: str,
        transform_func: Callable[[Any], Any],
        operation_name: str,
        new_columns: Optional[Dict[str, str]] = None,
    ) -> pd.DataFrame:
        """Apply transformation to a column with common error handling."""
        try:
            result_df = DataframeCleaner._validate_dataframe(df, operation_name)
            if len(result_df) == 0:
                return result_df

            if column_name not in result_df.columns:
                logger.warning(f"No {column_name} column found for {operation_name}")
                return result_df

            # Apply transformation
            transformed_data = result_df[column_name].apply(transform_func)

            # Handle single column transformation
            if new_columns is None:
                result_df[column_name] = transformed_data
            else:
                # Handle multi-column transformation
                for i, (new_col, _) in enumerate(new_columns.items()):
                    result_df[new_col] = [data[i] for data in transformed_data]

            logger.info(f"Successfully applied {operation_name}")
            return result_df

        except Exception as e:
            error_msg = f"Unexpected error in {operation_name}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

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
    def revenue_string_to_min_max(revenue: Union[str, float, Any]) -> Dict[str, str]:
        """
        Convert revenue string to min/max values.

        Args:
            revenue: String like "45k €⁄an", "380-580 €⁄j", "49k-60k €⁄an", or NaN/None

        Returns:
            Dict with 'min' and 'max' keys containing string values
        """
        if pd.isna(revenue) or not revenue or (isinstance(revenue, str) and revenue.strip() == ""):
            return {"min": "", "max": ""}

        revenue = str(revenue).strip()

        # Handle the specific case of space in numbers like "45 003-55k" -> "45-55k"
        # This handles cases where there's a space in the first number of a range
        revenue = re.sub(r"(\d+)\s+(\d+)(-\d+k)", r"\1\3", revenue, flags=re.IGNORECASE)

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

    @staticmethod
    def publication_date_cleaning(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean publication_date column by extracting dates and update dates.

        Handles formats like:
        - "Publiée le 06/08/2025" → publication_date: 2025-08-06, update_date: NaT
        - "Publiée le 21/07/2025 - Mise à jour le 23/07/2025" → publication_date: 2025-07-21, update_date: 2025-07-23
        - "" → publication_date: NaT, update_date: NaT
        """
        logger.info("Cleaning publication dates")

        def parse_publication_date(
            date_str,
        ) -> Tuple[Union[pd.Timestamp, Any], Union[pd.Timestamp, Any]]:
            if (
                pd.isna(date_str)
                or not date_str
                or (isinstance(date_str, str) and date_str.strip() == "")
            ):
                return pd.NaT, pd.NaT

            date_str = str(date_str).strip()

            # Check for update date pattern
            if " - Mise à jour le " in date_str:
                parts = date_str.split(" - Mise à jour le ")
                pub_part = parts[0]
                update_part = parts[1]

                # Extract publication date
                pub_match = re.search(r"Publiée le (\d{2}/\d{2}/\d{4})", pub_part)
                pub_date = (
                    pd.to_datetime(pub_match.group(1), format="%d/%m/%Y") if pub_match else pd.NaT
                )

                # Extract update date
                update_date = pd.to_datetime(update_part, format="%d/%m/%Y")

                return pub_date, update_date
            else:
                # Single publication date
                pub_match = re.search(r"Publiée le (\d{2}/\d{2}/\d{4})", date_str)
                pub_date = (
                    pd.to_datetime(pub_match.group(1), format="%d/%m/%Y") if pub_match else pd.NaT
                )
                return pub_date, pd.NaT

        # Initialize update_date column first
        result_df = DataframeCleaner._validate_dataframe(df, "publication date cleaning")
        if len(result_df) == 0:
            return result_df

        if "publication_date" not in result_df.columns:
            logger.warning("No publication_date column found")
            return result_df

        result_df["update_date"] = pd.NaT

        return DataframeCleaner._apply_column_transformation(
            result_df,
            "publication_date",
            parse_publication_date,
            "publication date cleaning",
            {"publication_date": "pub_date", "update_date": "update_date"},
        )

    @staticmethod
    def start_date_cleaning(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean start_date column by parsing dates and detecting ASAP indicators.

        Handles formats like:
        - "30/09/2025" → start_date: 2025-09-30, start_date_asap: False
        - "Dès que possible" → start_date: NaT, start_date_asap: True
        - "" → start_date: NaT, start_date_asap: NaT
        """
        logger.info("Cleaning start dates")

        def parse_start_date(date_str) -> Tuple[Union[pd.Timestamp, Any], Union[bool, Any]]:
            if (
                pd.isna(date_str)
                or not date_str
                or (isinstance(date_str, str) and date_str.strip() == "")
            ):
                return pd.NaT, pd.NA

            date_str = str(date_str).strip()

            # Check for ASAP indicators
            asap_indicators = [
                "dès que possible",
                "asap",
                "immédiatement",
                "immediately",
                "tout de suite",
                "maintenant",
                "disponible",
            ]

            if any(indicator in date_str.lower() for indicator in asap_indicators):
                return pd.NaT, True

            # Try to parse as date DD/MM/YYYY
            try:
                parsed_date = pd.to_datetime(date_str, format="%d/%m/%Y")
                return parsed_date, False
            except (ValueError, TypeError):
                # If parsing fails, treat as unknown
                return pd.NaT, pd.NA

        # Initialize start_date_asap column first
        result_df = DataframeCleaner._validate_dataframe(df, "start date cleaning")
        if len(result_df) == 0:
            return result_df

        if "start_date" not in result_df.columns:
            logger.warning("No start_date column found")
            return result_df

        result_df["start_date_asap"] = pd.NA

        return DataframeCleaner._apply_column_transformation(
            result_df,
            "start_date",
            parse_start_date,
            "start date cleaning",
            {"start_date": "parsed_date", "start_date_asap": "asap_flag"},
        )

    @staticmethod
    def standardize_duration(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize duration column by converting all formats to days.

        Handles formats like:
        - "145 jours" → 145.0 days
        - "12 mois" → 365.0 days (12 * 30.42 avg days/month)
        - "3 ans" → 1095.0 days (3 * 365)
        - "" → NaN
        """
        logger.info("Standardizing duration to days")

        def parse_duration(duration_str) -> Union[float, Any]:
            if (
                pd.isna(duration_str)
                or not duration_str
                or (isinstance(duration_str, str) and duration_str.strip() == "")
            ):
                return pd.NA

            duration_str = str(duration_str).strip().lower()

            # Extract number and unit
            match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)", duration_str)
            if not match:
                return pd.NA

            value = float(match.group(1))
            unit = match.group(2)

            # Convert to days
            if unit in ["jour", "jours", "day", "days", "j"]:
                return value
            elif unit in ["semaine", "semaines", "week", "weeks", "s"]:
                return value * 7
            elif unit in ["mois", "month", "months", "m"]:
                return value * 30  # Average days per month
            elif unit in ["an", "ans", "année", "années", "year", "years", "y"]:
                return value * 365
            else:
                # Unknown unit, return NaN
                return pd.NA

        result_df = DataframeCleaner._validate_dataframe(df, "duration standardization")
        if len(result_df) == 0:
            return result_df

        if "duration" not in result_df.columns:
            logger.warning("No duration column found")
            return result_df

        # Apply transformation and add new column
        result_df["duration_days"] = result_df["duration"].apply(parse_duration)

        logger.info("Successfully standardized duration to days")
        return result_df

    @staticmethod
    def parse_company_description(df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse company_description column to extract location, size, and type.

        Handles formats like:
        - "< 20 salariés , Cabinet de recrutement / placement" → size + type
        - "ESN" → type only
        - "Paris, France , 250 - 999 salariés , ESN" → location + size + type
        - "" → all NaN
        """
        logger.info("Parsing company descriptions")

        def parse_description(desc_str) -> Tuple[Union[str, Any], Union[str, Any], Union[str, Any]]:
            if (
                pd.isna(desc_str)
                or not desc_str
                or (isinstance(desc_str, str) and desc_str.strip() == "")
            ):
                return pd.NA, pd.NA, pd.NA

            desc_str = str(desc_str).strip()

            # Split by commas and clean whitespace
            parts = [part.strip() for part in desc_str.split(",")]
            # Remove empty parts
            parts = [part for part in parts if part]

            location = pd.NA
            size = pd.NA
            company_type = pd.NA

            if len(parts) == 4:
                # 4 parts: first 2 are location, third is size, fourth is type
                location = f"{parts[0]}, {parts[1]}"
                size = parts[2]
                company_type = parts[3]
            elif len(parts) == 3:
                # 3 parts: first is location, second is size, third is type
                location = parts[0]
                size = parts[1]
                company_type = parts[2]
            elif len(parts) == 2:
                # 2 parts: first is size, second is type
                size = parts[0]
                company_type = parts[1]
            elif len(parts) == 1:
                # 1 part: it's the type
                company_type = parts[0]

            return location, size, company_type

        # Initialize new columns first
        result_df = DataframeCleaner._validate_dataframe(df, "company description parsing")
        if len(result_df) == 0:
            return result_df

        if "company_description" not in result_df.columns:
            logger.warning("No company_description column found")
            return result_df

        result_df["company_location"] = pd.NA
        result_df["company_size"] = pd.NA
        result_df["company_type"] = pd.NA

        return DataframeCleaner._apply_column_transformation(
            result_df,
            "company_description",
            parse_description,
            "company description parsing",
            {"company_location": "location", "company_size": "size", "company_type": "type"},
        )

    @staticmethod
    def contract_types_one_hot_encoding(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert contract_types column to one-hot encoded boolean columns.

        Handles formats like:
        - "Freelance" → contract_Freelance: True, others: False
        - "CDI,CDD,Freelance" → contract_CDI: True, contract_CDD: True, contract_Freelance: True
        - "" → all contract columns: False
        """
        logger.info("Converting contract types to one-hot encoding")

        result_df = DataframeCleaner._validate_dataframe(df, "contract types one-hot encoding")
        if len(result_df) == 0:
            return result_df

        if "contract_types" not in result_df.columns:
            logger.warning("No contract_types column found")
            return result_df

        try:
            # Find all unique contract types in the dataset
            all_contract_types = set()
            for contract_str in result_df["contract_types"]:
                if (
                    not pd.isna(contract_str)
                    and contract_str
                    and (not isinstance(contract_str, str) or contract_str.strip())
                ):
                    contract_str = str(contract_str)
                    # Split by comma and clean whitespace
                    types = [t.strip() for t in contract_str.split(",")]
                    types = [t for t in types if t]  # Remove empty strings
                    all_contract_types.update(types)

            # Create boolean columns for each contract type
            for contract_type in all_contract_types:
                column_name = f"contract_{contract_type}"
                result_df[column_name] = False

            # Fill boolean columns based on contract_types values
            for idx, contract_str in enumerate(result_df["contract_types"]):
                if (
                    not pd.isna(contract_str)
                    and contract_str
                    and (not isinstance(contract_str, str) or contract_str.strip())
                ):
                    contract_str = str(contract_str)
                    # Split by comma and clean whitespace
                    types = [t.strip() for t in contract_str.split(",")]
                    types = [t for t in types if t]  # Remove empty strings

                    # Set corresponding boolean columns to True
                    for contract_type in types:
                        column_name = f"contract_{contract_type}"
                        if column_name in result_df.columns:
                            result_df.at[idx, column_name] = True

            logger.info(
                f"Successfully created one-hot encoding for {len(all_contract_types)} contract types"
            )
            return result_df

        except Exception as e:
            error_msg = f"Unexpected error creating contract types one-hot encoding: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
