import os
import tempfile

from JobOfferCleaner.CSVLoader import CSVLoader


class TestCSVToPandas:
    """
    Test class to test data loading, separator detection and proper error handling
    """

    def test_basic_csv_loading(self):
        csv_content = "name,age,city\nAlice,30,NYC\nBob,25,LA"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = CSVLoader.csv_to_pandas(temp_path)
            assert len(df) == 2
            assert list(df.columns) == ["name", "age", "city"]
            assert df.loc[0, "name"] == "Alice"
            assert df.loc[1, "age"] == 25
        finally:
            os.unlink(temp_path)
