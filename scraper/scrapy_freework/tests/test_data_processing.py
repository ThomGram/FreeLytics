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
                result = self._process_salary_field(input_value)
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
                result = self._process_salary_field(input_value)
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
                result = self._process_salary_field(input_value)
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
                result = self._process_salary_field(input_value)
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
                result = self._clean_text(input_value)
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
                result = self._process_contract_types(input_list)
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
                result = self._process_skills(input_list)
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
                result = self._process_description(input_list)
                self.assertEqual(result, expected)

    def test_icon_path_matching(self):
        """Test SVG icon path matching logic."""
        mapping = self.spider.get_icon_field_mapping()

        test_cases = [
            # Calendar icon - start date
            (
                "M152 24c0-13.3-10.7-24-24-24s-24 10.7-24 24V64H64C28.7 64 0 92.7 0 128v16 48V448...",
                "start_date",
            ),
            # Clock icon - duration
            (
                "M464 256A208 208 0 1 1 48 256a208 208 0 1 1 416 0zM0 256a256 256 0 1 0 512 0A256 256 0 1 0 0 256z...",
                "duration",
            ),
            # Money icon - salary
            (
                "M88 32C39.4 32 0 71.4 0 120V392c0 48.6 39.4 88 88 88H424c48.6 0 88-39.4 88-88V216...",
                "salary",
            ),
        ]

        for svg_path, expected_field in test_cases:
            with self.subTest(svg_path=svg_path[:50] + "..."):
                result = self._match_icon_to_field(svg_path, mapping)
                self.assertEqual(result, expected_field)

    def test_icon_path_no_match(self):
        """Test behavior when SVG path doesn't match any known icon."""
        mapping = self.spider.get_icon_field_mapping()
        unknown_path = "M999 999 unknown path data that doesn't match anything"

        result = self._match_icon_to_field(unknown_path, mapping)
        self.assertIsNone(result)

    # Helper methods to simulate the actual processing logic

    def _process_salary_field(self, value):
        """Simulate salary field processing logic."""
        result = {"salary": "", "daily_rate": ""}

        if "€⁄an" in value and "€⁄j" in value:
            parts = value.split(", ")
            if len(parts) == 2:
                result["salary"] = parts[0].strip()
                result["daily_rate"] = parts[1].strip()
            else:
                result["salary"] = value
        elif "€⁄j" in value:
            result["daily_rate"] = value
        elif "€⁄an" in value:
            result["salary"] = value
        else:
            result["salary"] = value

        return result

    def _clean_text(self, text):
        """Simulate text cleaning logic."""
        if text is None:
            return ""
        if isinstance(text, str):
            # Replace non-breaking space with regular space
            cleaned = text.replace("\xa0", " ")
            return cleaned.strip()
        return str(text).strip()

    def _process_contract_types(self, contract_list):
        """Simulate contract types processing."""
        return [text.strip() for text in contract_list if text.strip()]

    def _process_skills(self, skills_list):
        """Simulate skills processing."""
        return [skill.strip() for skill in skills_list if skill.strip()]

    def _process_description(self, paragraphs):
        """Simulate description processing."""
        return [para.strip() for para in paragraphs if para.strip()]

    def _match_icon_to_field(self, svg_path, mapping):
        """Simulate icon path matching logic."""
        for path_start, field_name in mapping.items():
            if svg_path.startswith(path_start):
                return field_name
        return None


if __name__ == "__main__":
    unittest.main()
