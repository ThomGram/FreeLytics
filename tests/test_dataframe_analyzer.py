import pandas as pd
import pytest

from src.job_offer_analyzer.DataframeAnalyzer import DataframeAnalyzer


class TestJobAnalyzer:
    """Test suite for job analytics functionality using TDD approach."""

    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing analytics."""
        return pd.DataFrame(
            {
                "job_title": [
                    "Data Scientist",
                    "Python Developer",
                    "DevOps Engineer",
                    "Data Analyst",
                    "Full Stack Developer",
                ],
                "job_category": ["Data Science", "Backend", "DevOps", "Data Science", "Full Stack"],
                "company_location": [
                    "Paris, France",
                    "Lyon, France",
                    "Paris, France",
                    "Marseille, France",
                    "Toulouse, France",
                ],
                "company_size": [
                    "100 - 249 salariés",
                    "< 20 salariés",
                    "> 1 000 salariés",
                    "250 - 999 salariés",
                    "50 - 99 salariés",
                ],
                "company_type": ["ESN", "Startup", "ESN", "Cabinet de recrutement", "ESN"],
                "contract_CDI": [True, False, True, True, False],
                "contract_Freelance": [False, True, False, False, True],
                "salary_min": ["45000", "50000", "", "40000", "48000"],
                "salary_max": ["55000", "60000", "", "45000", "55000"],
                "daily_rate_min": ["", "400", "500", "", "450"],
                "daily_rate_max": ["", "500", "600", "", "550"],
                "remote_work": ["Hybride", "Full Remote", "Présentiel", "Hybride", "Full Remote"],
                "start_date_asap": [True, False, True, False, False],
                "publication_date": [
                    pd.Timestamp("2024-01-15"),
                    pd.Timestamp("2024-01-20"),
                    pd.Timestamp("2024-01-10"),
                    pd.Timestamp("2024-01-25"),
                    pd.Timestamp("2024-01-18"),
                ],
                "start_date": [
                    pd.NaT,
                    pd.Timestamp("2024-03-01"),
                    pd.NaT,
                    pd.Timestamp("2024-02-15"),
                    pd.Timestamp("2024-02-20"),
                ],
                "duration_days": [365.0, 180.0, 730.0, 365.0, 270.0],
                "skills": [
                    "Python, SQL, Machine Learning",
                    "Python, Django, PostgreSQL",
                    "Docker, Kubernetes, AWS",
                    "SQL, Tableau, Excel",
                    "React, Node.js, MongoDB",
                ],
                "experience_required": ["3-5 ans", "Junior", "5+ ans", "1-3 ans", "2-4 ans"],
            }
        )

    # === SALARY MIN/MAX RANGE STATISTICS TESTS ===

    def test_get_salary_min_statistics_by_category(self, sample_job_data):
        """Test salary minimum statistics aggregation by job category."""
        analyzer = DataframeAnalyzer(sample_job_data)

        result = analyzer.get_salary_min_statistics_by_category()

        # Should return DataFrame with job categories as index
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have required statistical columns
        expected_columns = {"mean", "median", "min", "max", "count"}
        assert expected_columns.issubset(set(result.columns))

        # All statistical values should be numeric and positive
        for col in ["mean", "median", "min", "max"]:
            non_null_values = result[col].dropna()
            if len(non_null_values) > 0:
                assert (non_null_values >= 0).all()

        # Count should be integer and positive
        assert result["count"].dtype.kind in "iu"  # integer types
        assert (result["count"] > 0).all()

    def test_get_salary_max_statistics_by_category(self, sample_job_data):
        """Test salary maximum statistics aggregation by job category."""
        analyzer = DataframeAnalyzer(sample_job_data)

        result = analyzer.get_salary_max_statistics_by_category()

        # Should return DataFrame with job categories as index
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have required statistical columns
        expected_columns = {"mean", "median", "min", "max", "count"}
        assert expected_columns.issubset(set(result.columns))

        # All statistical values should be numeric and positive
        for col in ["mean", "median", "min", "max"]:
            non_null_values = result[col].dropna()
            if len(non_null_values) > 0:
                assert (non_null_values >= 0).all()

        # Count should be integer and positive
        assert result["count"].dtype.kind in "iu"  # integer types
        assert (result["count"] > 0).all()

    def test_get_daily_rate_min_statistics_by_category(self, sample_job_data):
        """Test daily rate minimum statistics aggregation by job category."""
        analyzer = DataframeAnalyzer(sample_job_data)

        result = analyzer.get_daily_rate_min_statistics_by_category()

        # Should return DataFrame with job categories as index
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have required statistical columns
        expected_columns = {"mean", "median", "min", "max", "count"}
        assert expected_columns.issubset(set(result.columns))

        # Statistical values should be numeric where not NaN
        for col in ["mean", "median", "min", "max"]:
            non_null_values = result[col].dropna()
            if len(non_null_values) > 0:
                assert (non_null_values >= 0).all()

    def test_get_daily_rate_max_statistics_by_category(self, sample_job_data):
        """Test daily rate maximum statistics aggregation by job category."""
        analyzer = DataframeAnalyzer(sample_job_data)

        result = analyzer.get_daily_rate_max_statistics_by_category()

        # Should return DataFrame with job categories as index
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have required statistical columns
        expected_columns = {"mean", "median", "min", "max", "count"}
        assert expected_columns.issubset(set(result.columns))

        # Statistical values should be numeric where not NaN
        for col in ["mean", "median", "min", "max"]:
            non_null_values = result[col].dropna()
            if len(non_null_values) > 0:
                assert (non_null_values >= 0).all()

    @pytest.fixture
    def revenue_by_category_data(self):
        """Fixture with diverse revenue data by job category for comprehensive testing."""
        return pd.DataFrame(
            {
                "job_category": [
                    "Data Science",
                    "Data Science",
                    "Data Science",
                    "Backend",
                    "Backend",
                    "DevOps",
                    "DevOps",
                    "DevOps",
                    "DevOps",
                ],
                "salary_min": ["40000", "50000", "60000", "45000", "55000", "", "", "", "48000"],
                "salary_max": ["45000", "55000", "70000", "50000", "65000", "", "", "", "52000"],
                "daily_rate_min": ["", "", "500", "400", "", "450", "500", "550", ""],
                "daily_rate_max": ["", "", "600", "500", "", "550", "600", "650", ""],
            }
        )

    def test_salary_min_statistics_comprehensive(self, revenue_by_category_data):
        """Test comprehensive salary minimum statistics calculation."""
        analyzer = DataframeAnalyzer(revenue_by_category_data)

        result = analyzer.get_salary_min_statistics_by_category()

        # Data Science category should have 3 entries with salary_min values
        ds_stats = result.loc["Data Science"]
        assert ds_stats["count"] == 3
        assert ds_stats["min"] == 40000.0  # Min of [40000, 50000, 60000]
        assert ds_stats["max"] == 60000.0  # Max of [40000, 50000, 60000]
        assert ds_stats["mean"] == pytest.approx(50000.0, rel=1e-2)  # (40000+50000+60000)/3

        # Backend category should have 2 entries
        backend_stats = result.loc["Backend"]
        assert backend_stats["count"] == 2
        assert backend_stats["min"] == 45000.0  # Min of [45000, 55000]
        assert backend_stats["max"] == 55000.0  # Max of [45000, 55000]

    def test_salary_max_statistics_comprehensive(self, revenue_by_category_data):
        """Test comprehensive salary maximum statistics calculation."""
        analyzer = DataframeAnalyzer(revenue_by_category_data)

        result = analyzer.get_salary_max_statistics_by_category()

        # Data Science category should have 3 entries with salary_max values
        ds_stats = result.loc["Data Science"]
        assert ds_stats["count"] == 3
        assert ds_stats["min"] == 45000.0  # Min of [45000, 55000, 70000]
        assert ds_stats["max"] == 70000.0  # Max of [45000, 55000, 70000]
        assert ds_stats["mean"] == pytest.approx(56666.67, rel=1e-2)  # (45000+55000+70000)/3

        # Backend category should have 2 entries
        backend_stats = result.loc["Backend"]
        assert backend_stats["count"] == 2
        assert backend_stats["min"] == 50000.0  # Min of [50000, 65000]
        assert backend_stats["max"] == 65000.0  # Max of [50000, 65000]

    def test_daily_rate_min_statistics_comprehensive(self, revenue_by_category_data):
        """Test comprehensive daily rate minimum statistics calculation."""
        analyzer = DataframeAnalyzer(revenue_by_category_data)

        result = analyzer.get_daily_rate_min_statistics_by_category()

        # DevOps should have daily rate minimums
        devops_stats = result.loc["DevOps"]
        assert devops_stats["count"] == 3  # 3 jobs with daily_rate_min values
        assert devops_stats["min"] == 450.0  # Min of [450, 500, 550]
        assert devops_stats["max"] == 550.0  # Max of [450, 500, 550]
        assert devops_stats["mean"] == pytest.approx(500.0, rel=1e-2)  # (450+500+550)/3

    def test_daily_rate_max_statistics_comprehensive(self, revenue_by_category_data):
        """Test comprehensive daily rate maximum statistics calculation."""
        analyzer = DataframeAnalyzer(revenue_by_category_data)

        result = analyzer.get_daily_rate_max_statistics_by_category()

        # DevOps should have daily rate maximums
        devops_stats = result.loc["DevOps"]
        assert devops_stats["count"] == 3  # 3 jobs with daily_rate_max values
        assert devops_stats["min"] == 550.0  # Min of [550, 600, 650]
        assert devops_stats["max"] == 650.0  # Max of [550, 600, 650]
        assert devops_stats["mean"] == pytest.approx(600.0, rel=1e-2)  # (550+600+650)/3

    @pytest.mark.parametrize(
        "category,expected_present",
        [
            ("Data Science", True),
            ("Backend", True),
            ("DevOps", True),
            ("NonExistent", False),
        ],
    )
    def test_category_presence_in_results(
        self, revenue_by_category_data, category, expected_present
    ):
        """Test that expected categories are present in results."""
        analyzer = DataframeAnalyzer(revenue_by_category_data)

        salary_min_result = analyzer.get_salary_min_statistics_by_category()
        salary_max_result = analyzer.get_salary_max_statistics_by_category()
        daily_rate_min_result = analyzer.get_daily_rate_min_statistics_by_category()
        daily_rate_max_result = analyzer.get_daily_rate_max_statistics_by_category()

        if expected_present:
            # Category should exist in at least one result
            in_salary_min = category in salary_min_result.index
            in_salary_max = category in salary_max_result.index
            in_daily_rate_min = category in daily_rate_min_result.index
            in_daily_rate_max = category in daily_rate_max_result.index
            assert in_salary_min or in_salary_max or in_daily_rate_min or in_daily_rate_max
        else:
            # Category should not exist in any result
            assert category not in salary_min_result.index
            assert category not in salary_max_result.index
            assert category not in daily_rate_min_result.index
            assert category not in daily_rate_max_result.index

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        analyzer = DataframeAnalyzer(empty_df)

        salary_min_result = analyzer.get_salary_min_statistics_by_category()
        salary_max_result = analyzer.get_salary_max_statistics_by_category()
        daily_rate_min_result = analyzer.get_daily_rate_min_statistics_by_category()
        daily_rate_max_result = analyzer.get_daily_rate_max_statistics_by_category()

        # Should return empty DataFrames with proper structure
        for result in [
            salary_min_result,
            salary_max_result,
            daily_rate_min_result,
            daily_rate_max_result,
        ]:
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_missing_columns_handling(self):
        """Test handling of DataFrame with missing required columns."""
        incomplete_df = pd.DataFrame(
            {"job_category": ["Data Science", "Backend"], "other_column": [1, 2]}
        )
        analyzer = DataframeAnalyzer(incomplete_df)

        salary_min_result = analyzer.get_salary_min_statistics_by_category()
        salary_max_result = analyzer.get_salary_max_statistics_by_category()
        daily_rate_min_result = analyzer.get_daily_rate_min_statistics_by_category()
        daily_rate_max_result = analyzer.get_daily_rate_max_statistics_by_category()

        # Should handle gracefully and return empty or minimal results
        for result in [
            salary_min_result,
            salary_max_result,
            daily_rate_min_result,
            daily_rate_max_result,
        ]:
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("statistic", ["mean", "median", "min", "max"])
    def test_statistical_methods_consistency(self, revenue_by_category_data, statistic):
        """Test that statistical methods produce consistent results."""
        analyzer = DataframeAnalyzer(revenue_by_category_data)

        # Test all four new methods
        results = [
            analyzer.get_salary_min_statistics_by_category(),
            analyzer.get_salary_max_statistics_by_category(),
            analyzer.get_daily_rate_min_statistics_by_category(),
            analyzer.get_daily_rate_max_statistics_by_category(),
        ]

        for result in results:
            # Statistical values should be consistent (min <= median <= max, etc.)
            for category in result.index:
                stats = result.loc[category]
                if not pd.isna(stats["min"]) and not pd.isna(stats["max"]):
                    assert stats["min"] <= stats["max"]
                if not pd.isna(stats["min"]) and not pd.isna(stats["median"]):
                    assert stats["min"] <= stats["median"]
                if not pd.isna(stats["median"]) and not pd.isna(stats["max"]):
                    assert stats["median"] <= stats["max"]
