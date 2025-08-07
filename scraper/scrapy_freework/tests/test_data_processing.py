import sys
import unittest
from pathlib import Path

from scrapy_freework.spiders.freework_spider import FreeworkSpider

# Add the parent directory to the path so we can import the spider
sys.path.append(str(Path(__file__).parent.parent))


class TestDataProcessing(unittest.TestCase):
    """Tests for data processing logic in FreeworkSpider."""

    def setUp(self):
        """Set up test fixtures."""
        self.spider = FreeworkSpider()

    def test_salary_tjm_splitting_both_present(self):
        """Test splitting when both salary and TJM are present."""
        test_cases = [
            ("45k-65k €⁄an, 400-650 €⁄j", ("45k-65k €⁄an", "400-650 €⁄j")),
            ("50k €⁄an, 500 €⁄j", ("50k €⁄an", "500 €⁄j")),
            ("35k-40k €⁄an, 350-400 €⁄j", ("35k-40k €⁄an", "350-400 €⁄j")),
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.spider._process_salary_field(input_value)
                self.assertEqual(result["salary"], expected[0])
                self.assertEqual(result["daily_rate"], expected[1])

    def test_salary_tjm_splitting_salary_only(self):
        """Test processing when only salary is present."""
        test_cases = [
            "45k-65k €⁄an",
            "50k €⁄an",
            "35000-45000 €⁄an",
        ]

        for input_value in test_cases:
            with self.subTest(input_value=input_value):
                result = self.spider._process_salary_field(input_value)
                self.assertEqual(result["salary"], input_value)
                self.assertEqual(result["daily_rate"], "")

    def test_salary_tjm_splitting_tjm_only(self):
        """Test processing when only TJM is present."""
        test_cases = [
            "400-650 €⁄j",
            "500 €⁄j",
            "350-400 €⁄j",
        ]

        for input_value in test_cases:
            with self.subTest(input_value=input_value):
                result = self.spider._process_salary_field(input_value)
                self.assertEqual(result["salary"], "")
                self.assertEqual(result["daily_rate"], input_value)

    def test_salary_tjm_splitting_malformed_combined(self):
        """Test processing of malformed combined salary/TJM values."""
        test_cases = [
            # No comma separator - should be treated as salary
            "45k-65k €⁄an 400-650 €⁄j",
            # Multiple commas - should use the whole string as salary
            "45k-65k €⁄an, 400-650 €⁄j, bonus",
        ]

        for input_value in test_cases:
            with self.subTest(input_value=input_value):
                result = self.spider._process_salary_field(input_value)
                self.assertEqual(result["salary"], input_value)
                self.assertEqual(result["daily_rate"], "")

    def test_text_cleaning_and_normalization(self):
        """Test text cleaning and normalization."""
        test_cases = [
            # Basic whitespace cleaning
            ("  Data Scientist  ", "Data Scientist"),
            ("\n  Senior Developer \t", "Senior Developer"),
            # Special characters normalization
            ("35k-40k\xa0€⁄an", "35k-40k €⁄an"),
            ("Dès que possible", "Dès que possible"),
            # Empty and None handling
            ("", ""),
            (None, ""),
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.spider._clean_text(input_value)
                self.assertEqual(result, expected)

    def test_contract_types_processing(self):
        """Test contract types extraction and cleaning."""
        test_cases = [
            (["CDI", "Freelance"], ["CDI", "Freelance"]),
            (["  CDI  ", " CDD ", ""], ["CDI", "CDD"]),  # With whitespace and empty
            ([], []),  # Empty list
            (
                ["Freelance", "freelance", "FREELANCE"],
                ["Freelance", "freelance", "FREELANCE"],
            ),  # Case variations
        ]

        for input_list, expected in test_cases:
            with self.subTest(input_list=input_list):
                result = self.spider._process_contract_types(input_list)
                self.assertEqual(result, expected)

    def test_skills_processing(self):
        """Test skills extraction and cleaning."""
        test_cases = [
            (["Python", "SQL", "Machine Learning"], ["Python", "SQL", "Machine Learning"]),
            (["  Python  ", " SQL ", ""], ["Python", "SQL"]),  # With whitespace and empty
            ([], []),  # Empty list
            (
                ["Python", "python", "PYTHON"],
                ["Python", "python", "PYTHON"],
            ),  # Case variations preserved
        ]

        for input_list, expected in test_cases:
            with self.subTest(input_list=input_list):
                result = self.spider._process_skills(input_list)
                self.assertEqual(result, expected)

    def test_description_processing(self):
        """Test description paragraph processing."""
        test_cases = [
            # Multiple paragraphs
            (
                [
                    "We are looking for a data scientist.",
                    "You will work on ML projects.",
                    "5+ years required.",
                ],
                [
                    "We are looking for a data scientist.",
                    "You will work on ML projects.",
                    "5+ years required.",
                ],
            ),
            # Paragraphs with whitespace
            (
                ["  First paragraph  ", "\n Second paragraph \t", ""],
                ["First paragraph", "Second paragraph"],
            ),
            # Empty input
            ([], []),
            # Single paragraph
            (["Single description paragraph."], ["Single description paragraph."]),
        ]

        for input_list, expected in test_cases:
            with self.subTest(input_list=input_list):
                result = self.spider._process_description(input_list)
                self.assertEqual(result, expected)

    def test_icon_path_matching(self):
        """Test SVG icon path matching logic."""
        mapping = self.spider.get_icon_field_mapping()

        test_cases = [
            # Calendar icon - start date
            (
                "M152 24c0-13.3-10.7-24-24-24s-24 10.7-24 24V64H64C28.7 64 0 92.7 0 128v16 48V448c0 35.3 28.7 64 64 64H384c35.3 0 64-28.7 64-64V192 144 128c0-35.3-28.7-64-64-64H344V24c0-13.3-10.7-24-24-24s-24 10.7-24 24V64H152V24zM48 192H400V448c0 8.8-7.2 16-16 16H64c-8.8 0-16-7.2-16-16V192z",
                "start_date",
            ),
            # Clock icon - duration
            (
                "M464 256A208 208 0 1 1 48 256a208 208 0 1 1 416 0zM0 256a256 256 0 1 0 512 0A256 256 0 1 0 0 256zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s-24 10.7-24 24z",
                "duration",
            ),
            # Money icon - salary
            (
                "M88 32C39.4 32 0 71.4 0 120V392c0 48.6 39.4 88 88 88H424c48.6 0 88-39.4 88-88V216c0-48.6-39.4-88-88-88H120c-13.3 0-24 10.7-24 24s10.7 24 24 24H424c22.1 0 40 17.9 40 40V392c0 22.1-17.9 40-40 40H88c-22.1 0-40-17.9-40-40V120c0-22.1 17.9-40 40-40H456c13.3 0 24-10.7 24-24s-10.7-24-24-24H88zM384 336a32 32 0 1 0 0-64 32 32 0 1 0 0 64z",
                "salary",
            ),
        ]

        for svg_path, expected_field in test_cases:
            with self.subTest(svg_path=svg_path[:50] + "..."):
                result = self.spider._match_icon_to_field(svg_path, mapping)
                self.assertEqual(result, expected_field)

    def test_icon_path_no_match(self):
        """Test behavior when SVG path doesn't match any known icon."""
        mapping = self.spider.get_icon_field_mapping()
        unknown_path = "M999 999 unknown path data that doesn't match anything"

        result = self.spider._match_icon_to_field(unknown_path, mapping)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
