import pytest

from src.scrapy_freework.scrapy_freework.spiders.freework_spider import FreeworkSpider


class TestDataProcessing:
    """Test suite for FreeworkSpider data processing using pytest best practices."""

    # === FIXTURES ===

    @pytest.fixture
    def spider(self):
        """FreeworkSpider instance for testing."""
        return FreeworkSpider()

    @pytest.fixture
    def icon_mapping(self, spider):
        """Icon to field mapping for testing."""
        return spider.get_icon_field_mapping()

    # === SALARY/TJM PROCESSING TESTS ===

    @pytest.mark.parametrize(
        "input_value,expected_salary,expected_daily_rate",
        [
            ("45k-65k €⁄an, 400-650 €⁄j", "45k-65k €⁄an", "400-650 €⁄j"),
            ("50k €⁄an, 500 €⁄j", "50k €⁄an", "500 €⁄j"),
            ("35k-40k €⁄an, 350-400 €⁄j", "35k-40k €⁄an", "350-400 €⁄j"),
        ],
    )
    def test_salary_tjm_splitting_both_present(
        self, spider, input_value, expected_salary, expected_daily_rate
    ):
        """Test splitting when both salary and TJM are present."""
        result = spider._process_salary_field(input_value)
        assert result["salary"] == expected_salary
        assert result["daily_rate"] == expected_daily_rate

    @pytest.mark.parametrize(
        "input_value",
        [
            "45k-65k €⁄an",
            "50k €⁄an",
            "35000-45000 €⁄an",
        ],
    )
    def test_salary_tjm_splitting_salary_only(self, spider, input_value):
        """Test processing when only salary is present."""
        result = spider._process_salary_field(input_value)
        assert result["salary"] == input_value
        assert result["daily_rate"] == ""

    @pytest.mark.parametrize(
        "input_value",
        [
            "400-650 €⁄j",
            "500 €⁄j",
            "350-400 €⁄j",
        ],
    )
    def test_salary_tjm_splitting_tjm_only(self, spider, input_value):
        """Test processing when only TJM is present."""
        result = spider._process_salary_field(input_value)
        assert result["salary"] == ""
        assert result["daily_rate"] == input_value

    @pytest.mark.parametrize(
        "input_value",
        [
            "45k-65k €⁄an 400-650 €⁄j",  # No comma separator
            "45k-65k €⁄an, 400-650 €⁄j, bonus",  # Multiple commas
        ],
    )
    def test_salary_tjm_splitting_malformed_combined(self, spider, input_value):
        """Test processing of malformed combined salary/TJM values."""
        result = spider._process_salary_field(input_value)
        assert result["salary"] == input_value
        assert result["daily_rate"] == ""

    # === TEXT CLEANING TESTS ===

    @pytest.mark.parametrize(
        "input_value,expected",
        [
            ("  Data Scientist  ", "Data Scientist"),
            ("\n  Senior Developer \t", "Senior Developer"),
            ("35k-40k\xa0€⁄an", "35k-40k €⁄an"),
            ("Dès que possible", "Dès que possible"),
            ("", ""),
            (None, ""),
        ],
    )
    def test_text_cleaning_and_normalization(self, spider, input_value, expected):
        """Test text cleaning and normalization."""
        result = spider._clean_text(input_value)
        assert result == expected

    # === CONTRACT TYPES PROCESSING TESTS ===

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            (["CDI", "Freelance"], ["CDI", "Freelance"]),
            (["  CDI  ", " CDD ", ""], ["CDI", "CDD"]),  # With whitespace and empty
            ([], []),  # Empty list
            (["Freelance", "freelance", "FREELANCE"], ["Freelance", "freelance", "FREELANCE"]),
        ],
    )
    def test_contract_types_processing(self, spider, input_list, expected):
        """Test contract types extraction and cleaning."""
        result = spider._process_contract_types(input_list)
        assert result == expected

    # === SKILLS PROCESSING TESTS ===

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            (["Python", "SQL", "Machine Learning"], ["Python", "SQL", "Machine Learning"]),
            (["  Python  ", " SQL ", ""], ["Python", "SQL"]),  # With whitespace and empty
            ([], []),  # Empty list
            (["Python", "python", "PYTHON"], ["Python", "python", "PYTHON"]),  # Case preserved
        ],
    )
    def test_skills_processing(self, spider, input_list, expected):
        """Test skills extraction and cleaning."""
        result = spider._process_skills(input_list)
        assert result == expected

    # === DESCRIPTION PROCESSING TESTS ===

    @pytest.mark.parametrize(
        "input_list,expected",
        [
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
            (
                ["  First paragraph  ", "\n Second paragraph \t", ""],
                ["First paragraph", "Second paragraph"],
            ),
            ([], []),
            (["Single description paragraph."], ["Single description paragraph."]),
        ],
    )
    def test_description_processing(self, spider, input_list, expected):
        """Test description paragraph processing."""
        result = spider._process_description(input_list)
        assert result == expected

    # === ICON MATCHING TESTS ===

    @pytest.mark.parametrize(
        "svg_path,expected_field",
        [
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
        ],
    )
    def test_icon_path_matching(self, spider, icon_mapping, svg_path, expected_field):
        """Test SVG icon path matching logic."""
        result = spider._match_icon_to_field(svg_path, icon_mapping)
        assert result == expected_field

    def test_icon_path_no_match(self, spider, icon_mapping):
        """Test behavior when SVG path doesn't match any known icon."""
        unknown_path = "M999 999 unknown path data that doesn't match anything"
        result = spider._match_icon_to_field(unknown_path, icon_mapping)
        assert result is None

    # === INTEGRATION TESTS ===

    def test_icon_field_mapping_functionality(self, spider):
        """Test that icon field mapping returns expected structure."""
        mapping = spider.get_icon_field_mapping()
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

        # Check that all values are valid field names
        valid_fields = {
            "start_date",
            "duration",
            "salary",
            "location",
            "contract_types",
            "skills",
            "experience",
            "remote_work",
        }
        for field in mapping.values():
            assert field in valid_fields

    def test_get_icon_field_mapping(self, spider):
        """Test icon field mapping structure and content."""
        mapping = spider.get_icon_field_mapping()

        # Should be a dictionary with SVG paths as keys and field names as values
        assert isinstance(mapping, dict)
        assert all(isinstance(k, str) for k in mapping.keys())
        assert all(isinstance(v, str) for v in mapping.values())

        # Should contain common field mappings
        expected_fields = {"start_date", "duration", "salary"}
        actual_fields = set(mapping.values())
        assert expected_fields.issubset(actual_fields)
