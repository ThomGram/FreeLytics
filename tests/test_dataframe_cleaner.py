import pandas as pd
import pytest

from src.job_offer_cleaner.DataframeCleaner import DataframeCleaner


class TestDataframeCleaner:
    """Test suite for DataframeCleaner using pytest best practices."""

    # === FIXTURES ===

    @pytest.fixture
    def duplicate_job_data(self):
        """Sample job data with duplicates for testing duplicate removal."""
        return pd.DataFrame(
            {
                "job_title": [
                    "Python Developer",
                    "Data Analyst",
                    "Python Developer",
                    "Python Developer",
                ],
                "job_url": ["url1", "url2", "url1", "url4"],
                "job_category": ["Tech", "Data", "Backend", "Backend"],
                "company_name": ["TechCorp", "DataInc", "TechCorp", "TechCorp"],
                "contract_types": ["CDI", "Freelance", "CDI", "CDI"],
                "description": [
                    "Python dev role",
                    "Data analysis",
                    "Python dev role",
                    "Python dev role",
                ],
                "location": ["Paris", "Lyon", "Paris", "Marseille"],
                "salary": ["50000", "45000", "50000", "50000"],
                "daily_rate": ["", "400", "", ""],
            }
        )

    @pytest.fixture
    def revenue_job_data(self):
        """Sample job data for testing revenue splitting."""
        return pd.DataFrame(
            {
                "job_title": ["Python Developer"] * 4,
                "location": ["Paris"] * 4,
                "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
                "daily_rate": ["380-580 €⁄j", "550 €⁄j", "", ""],
            }
        )

    @pytest.fixture
    def publication_date_data(self):
        """Sample job data for testing publication date cleaning."""
        return pd.DataFrame(
            {
                "job_title": ["Python Developer"] * 4,
                "location": ["Paris"] * 4,
                "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
                "publication_date": [
                    "Publiée le 06/08/2025",
                    "Publiée le 21/07/2025 - Mise à jour le 23/07/2025",
                    "",
                    "",
                ],
            }
        )

    @pytest.fixture
    def start_date_data(self):
        """Sample job data for testing start date cleaning."""
        return pd.DataFrame(
            {
                "job_title": ["Python Developer"] * 4,
                "location": ["Paris"] * 4,
                "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
                "start_date": ["Dès que possible", "30/09/2025", "", ""],
            }
        )

    @pytest.fixture
    def duration_data(self):
        """Sample job data for testing duration standardization."""
        return pd.DataFrame(
            {
                "job_title": ["Python Developer"] * 4,
                "location": ["Paris"] * 4,
                "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
                "duration": ["12 mois", "3 ans", "145 jours", ""],
            }
        )

    @pytest.fixture
    def company_description_data(self):
        """Sample job data for testing company description parsing."""
        return pd.DataFrame(
            {
                "job_title": ["Python Developer"] * 6,
                "company_description": [
                    "< 20 salariés , Cabinet de recrutement / placement",
                    "ESN",
                    "Paris, France , 250 - 999 salariés , ESN",
                    "Balma, Occitanie , > 1 000 salariés , ESN",
                    "100 - 249 salariés , Cabinet de recrutement / placement",
                    "",
                ],
            }
        )

    @pytest.fixture
    def contract_types_data(self):
        """Sample job data for testing contract types one-hot encoding."""
        return pd.DataFrame(
            {
                "job_title": ["Python Developer"] * 3,
                "contract_types": ["Freelance", "CDI,CDD,Freelance", ""],
            }
        )

    # === DUPLICATE REMOVAL TESTS ===

    def test_dataframe_duplicates_removal_all_columns(self, duplicate_job_data):
        """Test removing duplicates considering all columns."""
        result = DataframeCleaner.remove_duplicates(duplicate_job_data)
        assert len(result) == 4  # All rows are different when considering all columns

    def test_dataframe_duplicates_removal_ignore_category(self, duplicate_job_data):
        """Test removing duplicates ignoring job_category column."""
        result = DataframeCleaner.remove_duplicates(
            duplicate_job_data, ignore_columns=["job_category"]
        )
        assert len(result) == 3  # Rows 0,2 become duplicates
        assert "Python Developer" in result["job_title"].values
        assert "Data Analyst" in result["job_title"].values

    def test_dataframe_duplicates_removal_ignore_multiple(self, duplicate_job_data):
        """Test removing duplicates ignoring multiple columns."""
        result = DataframeCleaner.remove_duplicates(
            duplicate_job_data, ignore_columns=["job_category", "location"]
        )
        assert len(result) <= 3

    @pytest.mark.parametrize(
        "df_data,expected_len",
        [
            (pd.DataFrame(), 0),  # Empty DataFrame
            (
                pd.DataFrame(
                    {
                        "job_title": ["Python Developer", "Data Analyst"],
                        "company_name": ["TechCorp", "DataInc"],
                        "location": ["Paris", "Lyon"],
                    }
                ),
                2,
            ),  # No duplicates
            (
                pd.DataFrame(
                    {
                        "job_title": ["Python Developer"] * 3,
                        "company_name": ["TechCorp"] * 3,
                        "location": ["Paris"] * 3,
                    }
                ),
                1,
            ),  # All duplicates
        ],
    )
    def test_duplicate_removal_edge_cases(self, df_data, expected_len):
        """Test duplicate removal with edge cases."""
        result = DataframeCleaner.remove_duplicates(df_data)
        assert len(result) == expected_len

    # === REVENUE SPLITTING TESTS ===

    def test_split_revenue_to_min_max(self, revenue_job_data):
        """Test splitting revenue into min/max columns."""
        result = DataframeCleaner.split_revenue_to_min_max(revenue_job_data)

        # Row 0: "45k €⁄an", "380-580 €⁄j"
        assert result["salary_min"].iloc[0] == "45000"
        assert result["salary_max"].iloc[0] == "45000"
        assert result["daily_rate_min"].iloc[0] == "380"
        assert result["daily_rate_max"].iloc[0] == "580"

        # Row 1: "", "550 €⁄j"
        assert result["salary_min"].iloc[1] == ""
        assert result["salary_max"].iloc[1] == ""
        assert result["daily_rate_min"].iloc[1] == "550"
        assert result["daily_rate_max"].iloc[1] == "550"

        # Row 2: "49k-60k €⁄an", ""
        assert result["salary_min"].iloc[2] == "49000"
        assert result["salary_max"].iloc[2] == "60000"
        assert result["daily_rate_min"].iloc[2] == ""
        assert result["daily_rate_max"].iloc[2] == ""

        # Row 3: "", ""
        assert result["salary_min"].iloc[3] == ""
        assert result["salary_max"].iloc[3] == ""
        assert result["daily_rate_min"].iloc[3] == ""
        assert result["daily_rate_max"].iloc[3] == ""

    @pytest.mark.parametrize(
        "revenue_input,expected_output",
        [
            ("45k €⁄an", {"min": "45000", "max": "45000"}),
            ("380-580 €⁄j", {"min": "380", "max": "580"}),
            ("49k-60k €⁄an", {"min": "49000", "max": "60000"}),
            ("", {"min": "", "max": ""}),
            ("550 €⁄j", {"min": "550", "max": "550"}),
        ],
    )
    def test_revenue_string_to_min_max(self, revenue_input, expected_output):
        """Test individual revenue string parsing."""
        result = DataframeCleaner.revenue_string_to_min_max(revenue_input)
        assert result == expected_output

    # === DATE CLEANING TESTS ===

    def test_publication_date_cleaning(self, publication_date_data):
        """Test publication date cleaning with various formats."""
        result = DataframeCleaner.publication_date_cleaning(publication_date_data)

        # Row 0: Simple publication date
        assert result["publication_date"].iloc[0] == pd.Timestamp("2025-08-06")
        assert pd.isna(result["update_date"].iloc[0])

        # Row 1: Publication with update date
        assert result["publication_date"].iloc[1] == pd.Timestamp("2025-07-21")
        assert result["update_date"].iloc[1] == pd.Timestamp("2025-07-23")

        # Row 2: Empty string
        assert pd.isna(result["publication_date"].iloc[2])
        assert pd.isna(result["update_date"].iloc[2])

    def test_start_date_cleaning(self, start_date_data):
        """Test start date cleaning with ASAP detection."""
        result = DataframeCleaner.start_date_cleaning(start_date_data)

        # Row 0: ASAP
        assert pd.isna(result["start_date"].iloc[0])
        assert result["start_date_asap"].iloc[0] is True

        # Row 1: Specific date
        assert result["start_date"].iloc[1] == pd.Timestamp("2025-09-30")
        assert result["start_date_asap"].iloc[1] is False

        # Row 2: Empty string
        assert pd.isna(result["start_date"].iloc[2])
        assert pd.isna(result["start_date_asap"].iloc[2])

    # === DURATION TESTS ===

    def test_standardize_duration(self, duration_data):
        """Test duration standardization to days."""
        result = DataframeCleaner.standardize_duration(duration_data)

        assert result["duration_days"].iloc[0] == 360.0  # 12 months = 360 days
        assert result["duration_days"].iloc[1] == 1095.0  # 3 years = 1095 days
        assert result["duration_days"].iloc[2] == 145.0  # 145 days
        assert pd.isna(result["duration_days"].iloc[3])  # Empty string

    # === COMPANY DESCRIPTION TESTS ===

    def test_company_description_parsing(self, company_description_data):
        """Test company description parsing into location, size, type."""
        result = DataframeCleaner.parse_company_description(company_description_data)

        # Test each row according to positional parsing rules
        test_cases = [
            (0, None, "< 20 salariés", "Cabinet de recrutement / placement"),
            (1, None, None, "ESN"),
            (2, "Paris, France", "250 - 999 salariés", "ESN"),
            (3, "Balma, Occitanie", "> 1 000 salariés", "ESN"),
            (4, None, "100 - 249 salariés", "Cabinet de recrutement / placement"),
            (5, None, None, None),  # Empty string
        ]

        for row_idx, expected_location, expected_size, expected_type in test_cases:
            if expected_location is None:
                assert pd.isna(result["company_location"].iloc[row_idx])
            else:
                assert result["company_location"].iloc[row_idx] == expected_location

            if expected_size is None:
                assert pd.isna(result["company_size"].iloc[row_idx])
            else:
                assert result["company_size"].iloc[row_idx] == expected_size

            if expected_type is None:
                assert pd.isna(result["company_type"].iloc[row_idx])
            else:
                assert result["company_type"].iloc[row_idx] == expected_type

    # === CONTRACT TYPES TESTS ===

    def test_contract_types_one_hot_encoding(self, contract_types_data):
        """Test one-hot encoding of contract types."""
        result = DataframeCleaner.contract_types_one_hot_encoding(contract_types_data)

        # Check that boolean columns are created
        assert "contract_CDI" in result.columns
        assert "contract_CDD" in result.columns
        assert "contract_Freelance" in result.columns

        # Row 0: "Freelance"
        assert not result["contract_CDI"].iloc[0]
        assert not result["contract_CDD"].iloc[0]
        assert result["contract_Freelance"].iloc[0]

        # Row 1: "CDI,CDD,Freelance"
        assert result["contract_CDI"].iloc[1]
        assert result["contract_CDD"].iloc[1]
        assert result["contract_Freelance"].iloc[1]

        # Row 2: Empty string
        assert not result["contract_CDI"].iloc[2]
        assert not result["contract_CDD"].iloc[2]
        assert not result["contract_Freelance"].iloc[2]
