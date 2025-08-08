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
