import pandas as pd

from JobOfferCleaner.DataframeCleaner import DataframeCleaner


class TestDataframeCleaner:
    """
    Test class to test data cleaning:
        remove duplicates, split tjm into min and max, split salary into min and max,
        ensure noramlization of date, salary, tjm, localisation,
        Split the company and job description into relevant sections,
        Standardize descritpion
    """

    def test_dataframe_duplicates_removal(self):
        # Create realistic job data with duplicates
        job_data = {
            "job_title": [
                "Python Developer",
                "Data Analyst",
                "Python Developer",
                "Python Developer",
            ],
            "job_url": [
                "url1",
                "url2",
                "url1",
                "url4",
            ],  # Make rows 0,2 identical except job_category
            "job_category": [
                "Tech",
                "Data",
                "Backend",
                "Backend",
            ],  # Different categories for rows 0,2
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
        df = pd.DataFrame(job_data)

        # Test removing duplicates considering all columns - should keep 4 rows (all different)
        df_all_cols = DataframeCleaner.remove_duplicates(df)
        assert len(df_all_cols) == 4

        # Test ignoring job_category - rows 0,2 become duplicates (same url1, TechCorp, etc.)
        df_ignore_category = DataframeCleaner.remove_duplicates(df, ignore_columns=["job_category"])
        assert len(df_ignore_category) == 3  # One duplicate removed
        assert "Python Developer" in df_ignore_category["job_title"].values
        assert "Data Analyst" in df_ignore_category["job_title"].values

        # Test ignoring multiple columns - more duplicates should be found
        df_ignore_multi = DataframeCleaner.remove_duplicates(
            df, ignore_columns=["job_category", "location"]
        )
        assert len(df_ignore_multi) <= 3  # Should remove at least one duplicate

    def test_empty_dataframe(self):
        """Test remove_duplicates with empty DataFrame"""
        df = pd.DataFrame()
        result = DataframeCleaner.remove_duplicates(df)
        assert len(result) == 0

    def test_no_duplicates(self):
        """Test remove_duplicates with no actual duplicates"""
        job_data = {
            "job_title": ["Python Developer", "Data Analyst"],
            "company_name": ["TechCorp", "DataInc"],
            "location": ["Paris", "Lyon"],
        }
        df = pd.DataFrame(job_data)
        result = DataframeCleaner.remove_duplicates(df)
        assert len(result) == 2

    def test_all_duplicates(self):
        """Test remove_duplicates when all rows are identical"""
        job_data = {
            "job_title": ["Python Developer", "Python Developer", "Python Developer"],
            "company_name": ["TechCorp", "TechCorp", "TechCorp"],
            "location": ["Paris", "Paris", "Paris"],
        }
        df = pd.DataFrame(job_data)
        result = DataframeCleaner.remove_duplicates(df)
        assert len(result) == 1

    def test_split_pay(self):
        """Test function used to split the tjm and salary into min/max column."""
        job_data = {
            "job_title": [
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
            ],
            "location": ["Paris", "Paris", "Paris", "Paris"],
            "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
            "daily_rate": ["380-580 €⁄j", "550 €⁄j", "", ""],
        }
        df = pd.DataFrame(job_data)
        df = DataframeCleaner.split_revenue_to_min_max(df)
        assert df["salary_min"].iloc[0] == "45000"
        assert df["salary_max"].iloc[0] == "45000"
        assert df["daily_rate_min"].iloc[0] == "380"
        assert df["daily_rate_max"].iloc[0] == "580"

        assert df["salary_min"].iloc[1] == ""
        assert df["salary_max"].iloc[1] == ""
        assert df["daily_rate_min"].iloc[1] == "550"
        assert df["daily_rate_max"].iloc[1] == "550"

        assert df["salary_min"].iloc[2] == "49000"
        assert df["salary_max"].iloc[2] == "60000"
        assert df["daily_rate_min"].iloc[2] == ""
        assert df["daily_rate_max"].iloc[2] == ""

        assert df["salary_min"].iloc[3] == ""
        assert df["salary_max"].iloc[3] == ""
        assert df["daily_rate_min"].iloc[3] == ""
        assert df["daily_rate_max"].iloc[3] == ""

    def test_publication_date_cleaning(self):
        job_data = {
            "job_title": [
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
            ],
            "location": ["Paris", "Paris", "Paris", "Paris"],
            "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
            "publication_date": [
                "Publiée le 06/08/2025",
                "Publiée le 21/07/2025 - Mise à jour le 23/07/2025",
                "",
                "",
            ],
        }
        df = pd.DataFrame(job_data)
        df = DataframeCleaner.publication_date_cleaning(df)
        assert df["publication_date"].iloc[0] == pd.Timestamp("2025-08-06")
        assert pd.isna(df["update_date"].iloc[0])

        assert df["publication_date"].iloc[1] == pd.Timestamp("2025-07-21")
        assert df["update_date"].iloc[1] == pd.Timestamp("2025-07-23")

        assert pd.isna(df["publication_date"].iloc[2])
        assert pd.isna(df["update_date"].iloc[2])

    def test_start_date_cleaning(self):
        job_data = {
            "job_title": [
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
            ],
            "location": ["Paris", "Paris", "Paris", "Paris"],
            "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
            "start_date": ["Dès que possible", "30/09/2025", "", ""],
        }
        df = pd.DataFrame(job_data)
        df = DataframeCleaner.start_date_cleaning(df)
        assert pd.isna(df["start_date"].iloc[0])
        assert df["start_date_asap"].iloc[0] is True

        assert df["start_date"].iloc[1] == pd.Timestamp("2025-09-30")
        assert df["start_date_asap"].iloc[1] is False

        assert pd.isna(df["start_date"].iloc[2])
        assert pd.isna(df["start_date_asap"].iloc[2])

    def test_standardize_duration(self):
        job_data = {
            "job_title": [
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
            ],
            "location": ["Paris", "Paris", "Paris", "Paris"],
            "salary": ["45k €⁄an", "", "49k-60k €⁄an", ""],
            "duration": ["12 mois", "3 ans", "145 jours", ""],
        }
        df = pd.DataFrame(job_data)
        df = DataframeCleaner.standardize_duration(df)
        assert df["duration_days"].iloc[0] == 360.0  # "12 mois" = 360 days 30 days per month
        assert df["duration_days"].iloc[1] == 1095.0  # "3 ans" = 1095 days (3*365)
        assert df["duration_days"].iloc[2] == 145.0  # "145 jours"
        assert pd.isna(df["duration_days"].iloc[3])  # Empty string

    def test_company_description_parsing(self):
        job_data = {
            "job_title": [
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
                "Python Developer",
            ],
            "company_description": [
                "< 20 salariés , Cabinet de recrutement / placement",
                "ESN",
                "Paris, France , 250 - 999 salariés , ESN",
                "Balma, Occitanie , > 1 000 salariés , ESN",
                "100 - 249 salariés , Cabinet de recrutement / placement",
                "",
            ],
        }
        df = pd.DataFrame(job_data)
        df = DataframeCleaner.parse_company_description(df)

        # Row 0: "< 20 salariés , Cabinet de recrutement / placement"
        assert pd.isna(df["company_location"].iloc[0])
        assert df["company_size"].iloc[0] == "< 20 salariés"
        assert df["company_type"].iloc[0] == "Cabinet de recrutement / placement"

        # Row 1: "ESN"
        assert pd.isna(df["company_location"].iloc[1])
        assert pd.isna(df["company_size"].iloc[1])
        assert df["company_type"].iloc[1] == "ESN"

        # Row 2: "Paris, France , 250 - 999 salariés , ESN"
        assert df["company_location"].iloc[2] == "Paris, France"
        assert df["company_size"].iloc[2] == "250 - 999 salariés"
        assert df["company_type"].iloc[2] == "ESN"

        # Row 3: "Balma, Occitanie , > 1 000 salariés , ESN"
        assert df["company_location"].iloc[3] == "Balma, Occitanie"
        assert df["company_size"].iloc[3] == "> 1 000 salariés"
        assert df["company_type"].iloc[3] == "ESN"

        # Row 4: "100 - 249 salariés , Cabinet de recrutement / placement"
        assert pd.isna(df["company_location"].iloc[4])
        assert df["company_size"].iloc[4] == "100 - 249 salariés"
        assert df["company_type"].iloc[4] == "Cabinet de recrutement / placement"

        # Row 5: Empty string - all fields should be missing
        assert pd.isna(df["company_location"].iloc[5])
        assert pd.isna(df["company_size"].iloc[5])
        assert pd.isna(df["company_type"].iloc[5])

    def test_contract_types_one_hot_encoding(self):
        job_data = {
            "job_title": [
                "Python Developer",
                "Python Developer",
                "Python Developer",
            ],
            "contract_types": [
                "Freelance",
                "CDI,CDD,Freelance",
                "",
            ],
        }
        df = pd.DataFrame(job_data)
        df = DataframeCleaner.contract_types_one_hot_encoding(df)

        # Check that boolean columns are created for each contract type
        assert "contract_CDI" in df.columns
        assert "contract_CDD" in df.columns
        assert "contract_Freelance" in df.columns

        # Row 0: "Freelance"
        assert not df["contract_CDI"].iloc[0]
        assert not df["contract_CDD"].iloc[0]
        assert df["contract_Freelance"].iloc[0]

        # Row 1: "CDI,CDD,Freelance"
        assert df["contract_CDI"].iloc[1]
        assert df["contract_CDD"].iloc[1]
        assert df["contract_Freelance"].iloc[1]

        # Row 2: Empty string - all should be False
        assert not df["contract_CDI"].iloc[2]
        assert not df["contract_CDD"].iloc[2]
        assert not df["contract_Freelance"].iloc[2]
