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

    # === CATEGORICAL ANALYSIS TESTS ===

    @pytest.fixture
    def categorical_analysis_data(self):
        """Fixture with comprehensive categorical data for analysis."""
        return pd.DataFrame(
            {
                "job_category": [
                    "Data Science",
                    "Data Science",
                    "Data Science",
                    "Data Science",
                    "Backend",
                    "Backend",
                    "Backend",
                    "DevOps",
                    "DevOps",
                    "DevOps",
                ],
                "remote_work": [
                    "Full Remote",
                    "Hybride",
                    "Présentiel",
                    "Full Remote",
                    "Hybride",
                    "Présentiel",
                    "Full Remote",
                    "Full Remote",
                    "Hybride",
                    "Présentiel",
                ],
                "experience_required": [
                    "3-5 ans",
                    "Junior",
                    "5+ ans",
                    "1-3 ans",
                    "Junior",
                    "3-5 ans",
                    "5+ ans",
                    "5+ ans",
                    "3-5 ans",
                    "1-3 ans",
                ],
                "skills": [
                    "Python, SQL, Machine Learning, AWS",
                    "Python, Django, PostgreSQL, Docker",
                    "R, Python, Tableau, Azure",
                    "Python, Spark, Kafka, GCP",
                    "Java, Spring, PostgreSQL, AWS",
                    "Node.js, Express, MongoDB",
                    "Python, FastAPI, Redis, Azure",
                    "Docker, Kubernetes, AWS, Terraform",
                    "Jenkins, GitLab, Azure, Ansible",
                    "Prometheus, Grafana, GCP, Helm",
                ],
            }
        )

    def test_get_remote_work_proportions_by_category(self, categorical_analysis_data):
        """Test remote work proportions by job category."""
        analyzer = DataframeAnalyzer(categorical_analysis_data)

        result = analyzer.get_remote_work_proportions_by_category()

        # Should return DataFrame with job categories as index
        assert isinstance(result, pd.DataFrame)
        assert "Data Science" in result.index
        assert "Backend" in result.index
        assert "DevOps" in result.index

        # Should have remote work type columns
        expected_columns = {"Full Remote", "Hybride", "Présentiel"}
        assert expected_columns.issubset(set(result.columns))

        # Proportions should sum to 1.0 for each category (allowing for floating point precision)
        for category in result.index:
            row_sum = result.loc[category].sum()
            assert abs(row_sum - 1.0) < 0.01

        # All values should be between 0 and 1
        assert (result >= 0).all().all()
        assert (result <= 1).all().all()

        # Data Science category: 2/4 Full Remote (0.5), 1/4 Hybride (0.25), 1/4 Présentiel (0.25)
        ds_props = result.loc["Data Science"]
        assert abs(ds_props["Full Remote"] - 0.5) < 0.01
        assert abs(ds_props["Hybride"] - 0.25) < 0.01
        assert abs(ds_props["Présentiel"] - 0.25) < 0.01

    def test_get_experience_proportions_by_category(self, categorical_analysis_data):
        """Test experience proportions by job category."""
        analyzer = DataframeAnalyzer(categorical_analysis_data)

        result = analyzer.get_experience_proportions_by_category()

        # Should return DataFrame with job categories as index
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have experience level columns
        expected_columns = {"Junior", "1-3 ans", "3-5 ans", "5+ ans"}
        assert expected_columns.issubset(set(result.columns))

        # Proportions should sum to 1.0 for each category
        for category in result.index:
            row_sum = result.loc[category].sum()
            assert abs(row_sum - 1.0) < 0.01

        # All values should be between 0 and 1
        assert (result >= 0).all().all()
        assert (result <= 1).all().all()

    def test_get_skills_frequency_by_category(self, categorical_analysis_data):
        """Test skills frequency analysis by job category."""
        analyzer = DataframeAnalyzer(categorical_analysis_data)

        result = analyzer.get_skills_frequency_by_category()

        # Should return DataFrame with job categories and skills
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have required columns
        expected_columns = {"job_category", "skill", "frequency", "proportion"}
        assert expected_columns.issubset(set(result.columns))

        # Frequency should be integer counts
        assert result["frequency"].dtype.kind in "iu"
        assert (result["frequency"] > 0).all()

        # Proportions should be between 0 and 1
        assert (result["proportion"] > 0).all()
        assert (result["proportion"] <= 1).all()

        # Check that Python appears in Data Science category
        ds_python = result[
            (result["job_category"] == "Data Science") & (result["skill"] == "Python")
        ]
        assert len(ds_python) > 0
        assert ds_python["frequency"].iloc[0] == 4  # Python appears in all 4 Data Science jobs

    def test_get_cloud_provider_frequency_by_category(self, categorical_analysis_data):
        """Test cloud provider frequency analysis by job category."""
        analyzer = DataframeAnalyzer(categorical_analysis_data)

        result = analyzer.get_cloud_provider_frequency_by_category()

        # Should return DataFrame with job categories and cloud providers
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Should have required columns
        expected_columns = {"job_category", "cloud_provider", "frequency", "proportion"}
        assert expected_columns.issubset(set(result.columns))

        # Should contain the major cloud providers
        cloud_providers = set(result["cloud_provider"].unique())
        expected_providers = {"AWS", "Azure", "GCP"}
        assert expected_providers.issubset(cloud_providers)

        # Frequency should be integer counts
        assert result["frequency"].dtype.kind in "iu"
        assert (result["frequency"] > 0).all()

        # Proportions should be between 0 and 1
        assert (result["proportion"] > 0).all()
        assert (result["proportion"] <= 1).all()

        # Check specific data: AWS appears twice in Data Science (out of 4 jobs)
        ds_aws = result[
            (result["job_category"] == "Data Science") & (result["cloud_provider"] == "AWS")
        ]
        assert len(ds_aws) > 0
        assert ds_aws["frequency"].iloc[0] == 1  # AWS appears 1 time in 4 Data Science jobs

    def test_empty_dataframe_categorical_analysis(self):
        """Test categorical analysis methods with empty DataFrame."""
        empty_df = pd.DataFrame()
        analyzer = DataframeAnalyzer(empty_df)

        # All methods should handle empty DataFrames gracefully
        remote_result = analyzer.get_remote_work_proportions_by_category()
        exp_result = analyzer.get_experience_proportions_by_category()
        skills_result = analyzer.get_skills_frequency_by_category()
        cloud_result = analyzer.get_cloud_provider_frequency_by_category()

        for result in [remote_result, exp_result, skills_result, cloud_result]:
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_missing_columns_categorical_analysis(self):
        """Test categorical analysis methods with missing columns."""
        incomplete_df = pd.DataFrame(
            {"job_category": ["Data Science", "Backend"], "other_column": [1, 2]}
        )
        analyzer = DataframeAnalyzer(incomplete_df)

        # Should handle gracefully when required columns are missing
        remote_result = analyzer.get_remote_work_proportions_by_category()
        exp_result = analyzer.get_experience_proportions_by_category()
        skills_result = analyzer.get_skills_frequency_by_category()
        cloud_result = analyzer.get_cloud_provider_frequency_by_category()

        for result in [remote_result, exp_result, skills_result, cloud_result]:
            assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize(
        "category,expected_present",
        [
            ("Data Science", True),
            ("Backend", True),
            ("DevOps", True),
            ("NonExistent", False),
        ],
    )
    def test_categorical_analysis_category_presence(
        self, categorical_analysis_data, category, expected_present
    ):
        """Test that expected categories are present in categorical analysis results."""
        analyzer = DataframeAnalyzer(categorical_analysis_data)

        remote_result = analyzer.get_remote_work_proportions_by_category()
        exp_result = analyzer.get_experience_proportions_by_category()

        if expected_present:
            assert category in remote_result.index
            assert category in exp_result.index
        else:
            assert category not in remote_result.index
            assert category not in exp_result.index
