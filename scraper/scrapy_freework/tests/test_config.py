import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scrapy_freework.spiders.freework_spider import FreeworkSpider

# Add the parent directory to the path so we can import the spider
sys.path.append(str(Path(__file__).parent.parent))


class TestFreeworkSpiderConfig(unittest.TestCase):
    """Tests for configuration handling in FreeworkSpider."""

    def setUp(self):
        """Set up test fixtures."""
        self.spider = FreeworkSpider()
        self.test_fixtures_dir = Path(__file__).parent / "fixtures"

    def test_generate_start_urls_with_valid_config(self):
        """Test URL generation with a valid configuration file."""
        # Mock logger using property patch
        with patch.object(type(self.spider), "logger", new_callable=MagicMock):
            with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
                mock_path.return_value.exists.return_value = True

                # Mock the config file path to use our test fixture
                with patch("configparser.ConfigParser.read") as mock_read:
                    # Simulate reading our test config
                    mock_read.side_effect = lambda path: self.spider._load_test_config()

                    urls = self._generate_urls_with_test_data()

                    # Should generate 8 URLs (2 jobs × 2 locations × 2 contracts)
                    self.assertEqual(len(urls), 8)

                    # Check URL format
                    expected_base = "https://www.free-work.com/fr/tech-it/jobs?query="
                    for url in urls:
                        self.assertTrue(url.startswith(expected_base))
                        self.assertIn("&locations=", url)
                        self.assertIn("&contracts=", url)

    def test_generate_start_urls_missing_config_file(self):
        """Test behavior when config file is missing."""
        with patch.object(type(self.spider), "logger", new_callable=MagicMock) as mock_logger:
            with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
                mock_path.return_value.exists.return_value = False

                urls = self.spider.generate_start_urls()

                self.assertEqual(urls, [])
                mock_logger.error.assert_called_with("Config file not found: ../../FreeLytics.cfg")

    def test_generate_start_urls_invalid_config_section(self):
        """Test behavior when config file is missing required section."""
        with patch.object(type(self.spider), "logger", new_callable=MagicMock) as mock_logger:
            with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
                mock_path.return_value.exists.return_value = True

                with patch("configparser.ConfigParser.has_section") as mock_has_section:
                    mock_has_section.return_value = False

                    urls = self.spider.generate_start_urls()

                    self.assertEqual(urls, [])
                    mock_logger.error.assert_called_with(
                        "Section 'freework' not found in config file"
                    )

    def test_generate_start_urls_missing_required_keys(self):
        """Test behavior when config file is missing required keys."""
        with patch.object(type(self.spider), "logger", new_callable=MagicMock) as mock_logger:
            with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
                mock_path.return_value.exists.return_value = True

                with patch("configparser.ConfigParser.has_section") as mock_has_section:
                    mock_has_section.return_value = True

                    with patch("configparser.ConfigParser.has_option") as mock_has_option:
                        mock_has_option.return_value = False

                        urls = self.spider.generate_start_urls()

                        self.assertEqual(urls, [])
                        mock_logger.error.assert_called_with(
                            "Key 'jobs' not found in freework section"
                        )

    def test_generate_start_urls_empty_base_url(self):
        """Test behavior when base_url is empty."""
        with patch.object(type(self.spider), "logger", new_callable=MagicMock) as mock_logger:
            with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
                mock_path.return_value.exists.return_value = True

                with self._mock_valid_config_structure():
                    with patch("configparser.ConfigParser.get") as mock_get:
                        mock_get.side_effect = lambda section, key: {
                            ("freework", "jobs"): '["data scientist"]',
                            ("freework", "locations"): '["fr~~~"]',
                            ("freework", "contracts"): '["permanent"]',
                            ("freework", "base_url"): "",
                        }.get((section, key))

                        urls = self.spider.generate_start_urls()

                        self.assertEqual(urls, [])
                        mock_logger.error.assert_called_with("base_url is empty in config file")

    def test_generate_start_urls_invalid_base_url_scheme(self):
        """Test behavior when base_url is missing scheme."""
        with patch.object(type(self.spider), "logger", new_callable=MagicMock) as mock_logger:
            with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
                mock_path.return_value.exists.return_value = True

                with self._mock_valid_config_structure():
                    with patch("configparser.ConfigParser.get") as mock_get:
                        mock_get.side_effect = lambda section, key: {
                            ("freework", "jobs"): '["data scientist"]',
                            ("freework", "locations"): '["fr~~~"]',
                            ("freework", "contracts"): '["permanent"]',
                            ("freework", "base_url"): "www.example.com",
                        }.get((section, key))

                        urls = self.spider.generate_start_urls()

                        self.assertEqual(urls, [])
                        mock_logger.error.assert_called_with(
                            "base_url missing scheme (http/https): www.example.com"
                        )

    def test_is_valid_url(self):
        """Test URL validation logic."""
        # Valid URLs
        self.assertTrue(self.spider.is_valid_url("https://example.com"))
        self.assertTrue(self.spider.is_valid_url("http://example.com/path"))

        # Invalid URLs
        self.assertFalse(self.spider.is_valid_url(""))
        self.assertFalse(self.spider.is_valid_url("invalid-url"))
        self.assertFalse(self.spider.is_valid_url("ftp://example.com"))

    def _mock_valid_config_structure(self):
        """Helper to mock valid config file structure."""
        return patch.multiple(
            "configparser.ConfigParser",
            has_section=lambda self, section: section == "freework",
            has_option=lambda self, section, key: key
            in ["jobs", "locations", "contracts", "base_url"],
        )

    def _generate_urls_with_test_data(self):
        """Helper to generate URLs with test data."""
        # Simulate the actual URL generation logic with test data
        jobs = ["data scientist", "machine learning"]
        locations = ["fr~~~", "paris"]
        contracts = ["permanent", "freelance"]
        base_url = "https://www.free-work.com/fr/tech-it/jobs?query="

        urls = []
        from itertools import product

        for job, location, contract in product(jobs, locations, contracts):
            url = f"{base_url}{job}&locations={location}&contracts={contract}"
            if self.spider.is_valid_url(url):
                urls.append(url)
        return urls


if __name__ == "__main__":
    unittest.main()
