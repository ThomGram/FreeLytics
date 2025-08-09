import pandas as pd


class DataframeAnalyzer:
    """Analytics class for job market data using pandas DataFrames."""

    def __init__(self, df):
        """Initialize analyzer with job data DataFrame.

        Args:
            df: pandas DataFrame containing job market data
        """
        self.df = df.copy() if not df.empty else df

    def _get_statistics_by_category(self, column_name: str) -> pd.DataFrame:
        """Generic method to calculate statistics for any revenue column by job category.

        Args:
            column_name: Name of the column to analyze (e.g., 'salary_min', 'daily_rate_max')

        Returns:
            DataFrame with statistics (mean, median, min, max, count) by job_category
        """
        if self.df.empty or "job_category" not in self.df.columns:
            return pd.DataFrame(columns=["mean", "median", "min", "max", "count"])

        # Extract values from the specified column
        data = []

        for idx, row in self.df.iterrows():
            category = row.get("job_category")
            if pd.isna(category):
                continue

            # Add column value if present and not empty
            if column_name in row and row[column_name] and str(row[column_name]).strip():
                try:
                    value = float(row[column_name])
                    data.append({"job_category": category, column_name: value, "job_id": idx})
                except (ValueError, TypeError):
                    pass

        if not data:
            return pd.DataFrame(columns=["mean", "median", "min", "max", "count"])

        data_df = pd.DataFrame(data)

        # Calculate statistics
        stats = (
            data_df.groupby("job_category")[column_name]
            .agg(
                [
                    ("mean", "mean"),
                    ("median", "median"),
                    ("min", "min"),
                    ("max", "max"),
                    ("count", "count"),
                ]
            )
            .round(2)
        )

        return stats

    def get_salary_min_statistics_by_category(self):
        """Calculate salary minimum statistics grouped by job category.

        Returns:
            DataFrame with statistics (mean, median, min, max, count) for salary_min by job_category
        """
        return self._get_statistics_by_category("salary_min")

    def get_salary_max_statistics_by_category(self):
        """Calculate salary maximum statistics grouped by job category.

        Returns:
            DataFrame with statistics (mean, median, min, max, count) for salary_max by job_category
        """
        return self._get_statistics_by_category("salary_max")

    def get_daily_rate_min_statistics_by_category(self):
        """Calculate daily rate minimum statistics grouped by job category.

        Returns:
            DataFrame with statistics (mean, median, min, max, count) for daily_rate_min by job_category
        """
        return self._get_statistics_by_category("daily_rate_min")

    def get_daily_rate_max_statistics_by_category(self):
        """Calculate daily rate maximum statistics grouped by job category.

        Returns:
            DataFrame with statistics (mean, median, min, max, count) for daily_rate_max by job_category
        """
        return self._get_statistics_by_category("daily_rate_max")
