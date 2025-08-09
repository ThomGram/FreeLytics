from typing import List, Optional

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

    def _get_proportions_by_category(self, column_name: str) -> pd.DataFrame:
        """Generic method to calculate proportions of categorical values by job category.

        Args:
            column_name: Name of the categorical column to analyze

        Returns:
            DataFrame with proportions by job_category (rows sum to 1.0)
        """
        if (
            self.df.empty
            or "job_category" not in self.df.columns
            or column_name not in self.df.columns
        ):
            return pd.DataFrame()

        # Create contingency table (cross-tabulation)
        contingency_table = pd.crosstab(self.df["job_category"], self.df[column_name])

        # Convert counts to proportions (normalize by rows)
        proportions = contingency_table.div(contingency_table.sum(axis=1), axis=0).fillna(0)

        return proportions.round(4)

    def _get_frequency_analysis(
        self,
        column_name: str,
        split_values: bool = False,
        filter_values: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Generic method to analyze frequency of values (optionally split by delimiters) by job category.

        Args:
            column_name: Name of the column to analyze
            split_values: Whether to split values by comma/delimiter
            filter_values: Optional list to filter for specific values only

        Returns:
            DataFrame with columns: job_category, {column_name}, frequency, proportion
        """
        if (
            self.df.empty
            or "job_category" not in self.df.columns
            or column_name not in self.df.columns
        ):
            return pd.DataFrame(columns=["job_category", column_name, "frequency", "proportion"])

        results = []

        for category in self.df["job_category"].unique():
            if pd.isna(category):
                continue

            category_data = self.df[self.df["job_category"] == category]
            total_jobs = len(category_data)

            # Count occurrences of each value
            value_counts: dict[str, int] = {}

            for _, row in category_data.iterrows():
                cell_value = row[column_name]
                if pd.isna(cell_value) or not cell_value:
                    continue

                if split_values:
                    # Split by comma and clean whitespace
                    values = [v.strip() for v in str(cell_value).split(",") if v.strip()]
                else:
                    values = [str(cell_value).strip()]

                for value in values:
                    if filter_values and value not in filter_values:
                        continue
                    value_counts[value] = value_counts.get(value, 0) + 1

            # Create result rows
            for value, count in value_counts.items():
                proportion = count / total_jobs
                results.append(
                    {
                        "job_category": category,
                        column_name: value,
                        "frequency": count,
                        "proportion": round(proportion, 4),
                    }
                )

        if not results:
            return pd.DataFrame(columns=["job_category", column_name, "frequency", "proportion"])

        return pd.DataFrame(results).sort_values(
            ["job_category", "frequency"], ascending=[True, False]
        )

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

    # === CATEGORICAL ANALYSIS METHODS ===

    def get_remote_work_proportions_by_category(self) -> pd.DataFrame:
        """Calculate remote work proportions by job category.

        Returns:
            DataFrame with proportions of remote work types by job_category
        """
        return self._get_proportions_by_category("remote_work")

    def get_experience_proportions_by_category(self) -> pd.DataFrame:
        """Calculate experience level proportions by job category.

        Returns:
            DataFrame with proportions of experience levels by job_category
        """
        return self._get_proportions_by_category("experience_required")

    def get_skills_frequency_by_category(self) -> pd.DataFrame:
        """Calculate skills frequency analysis by job category.

        Returns:
            DataFrame with columns: job_category, skill, frequency, proportion
        """
        result = self._get_frequency_analysis("skills", split_values=True)
        # Rename column to match expected test format
        if "skills" in result.columns:
            result = result.rename(columns={"skills": "skill"})
        return result

    def get_cloud_provider_frequency_by_category(self) -> pd.DataFrame:
        """Calculate cloud provider frequency analysis by job category.

        Returns:
            DataFrame with columns: job_category, cloud_provider, frequency, proportion
        """
        cloud_providers = ["AWS", "Azure", "GCP"]
        result = self._get_frequency_analysis(
            "skills", split_values=True, filter_values=cloud_providers
        )
        # Rename column to match expected test format
        if "skills" in result.columns:
            result = result.rename(columns={"skills": "cloud_provider"})
        return result
