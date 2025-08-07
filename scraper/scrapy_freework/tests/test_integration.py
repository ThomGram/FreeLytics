import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy_freework.spiders.freework_spider import FreeworkSpider

# Add the parent directory to the path so we can import the spider
sys.path.append(str(Path(__file__).parent.parent))


class TestFreeworkSpiderIntegration(unittest.TestCase):
    """Integration tests for FreeworkSpider end-to-end functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.spider = FreeworkSpider()
        self.test_fixtures_dir = Path(__file__).parent / "fixtures"

    def _create_response(self, html_file, url="http://example.com"):
        """Helper to create a Scrapy response from HTML fixture."""
        html_path = self.test_fixtures_dir / html_file
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        return HtmlResponse(url=url, body=html_content.encode("utf-8"), encoding="utf-8")

    def test_end_to_end_scraping_workflow(self):
        """Test the complete scraping workflow from listing to job details."""
        # Step 1: Parse job listing page
        listing_response = self._create_response("job_listing_page.html", "http://example.com/jobs")

        # Get requests generated from listing page
        requests = list(self.spider.parse(listing_response))

        # Should generate one request for job detail
        self.assertEqual(len(requests), 1)
        detail_request = requests[0]
        self.assertIsInstance(detail_request, Request)

        # Step 2: Parse job detail page
        detail_response = self._create_response("job_detail_full.html", detail_request.url)

        # Process the job detail
        jobs = list(self.spider.parse_job_detail(detail_response))

        # Should yield one complete job item
        self.assertEqual(len(jobs), 1)

        job = jobs[0]
        self._assert_complete_job_data(job)

    def test_start_requests_integration(self):
        """Test start_requests integration with URL generation."""
        # Mock the config file to exist and provide valid data
        with patch("scrapy_freework.spiders.freework_spider.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("configparser.ConfigParser") as mock_config:
                # Mock config parser
                config_instance = MagicMock()
                mock_config.return_value = config_instance

                config_instance.has_section.return_value = True
                config_instance.has_option.return_value = True
                config_instance.get.side_effect = lambda section, key: {
                    "jobs": '["data scientist"]',
                    "locations": '["fr~~~"]',
                    "contracts": '["permanent"]',
                    "base_url": "https://www.free-work.com/fr/tech-it/jobs?query=",
                }.get(key)

                # Generate start requests
                requests = list(self.spider.start_requests())

                # Should generate one request
                self.assertEqual(len(requests), 1)

                request = requests[0]
                self.assertIsInstance(request, Request)
                self.assertEqual(request.callback, self.spider.parse)
                self.assertIn("data scientist", request.url)
                self.assertIn("fr~~~", request.url)
                self.assertIn("permanent", request.url)

    def test_pagination_workflow(self):
        """Test pagination handling (when implemented)."""
        # Create a mock response with pagination info
        listing_response = self._create_response("job_listing_page.html")

        # Test get_total_pages_simple method
        with patch.object(listing_response, "css") as mock_css:
            # Mock pagination container
            mock_container = MagicMock()
            mock_container.css.side_effect = [
                MagicMock(get=lambda: 100),  # total-items
                MagicMock(get=lambda: 16),  # items-per-page
            ]
            mock_css.return_value = mock_container

            total_pages = self.spider.get_total_pages_simple(listing_response)

            # Should calculate correct number of pages (100/16 = 7 pages)
            import math

            expected_pages = math.ceil(100 / 16)
            self.assertEqual(total_pages, expected_pages)

    def test_error_handling_integration(self):
        """Test error handling across the scraping workflow."""
        # Test with malformed HTML
        malformed_response = HtmlResponse(
            url="http://example.com", body=b"<html><body><h1>Malformed", encoding="utf-8"
        )

        # Should handle parsing errors gracefully
        with self.assertLogs(level="ERROR"):
            jobs = list(self.spider.parse_job_detail(malformed_response))

            # Should still yield a result with error information
            self.assertEqual(len(jobs), 1)
            job = jobs[0]
            self.assertIn("error", job)

    def test_complete_data_extraction_integration(self):
        """Test that all expected fields are extracted and processed correctly."""
        detail_response = self._create_response("job_detail_full.html")

        jobs = list(self.spider.parse_job_detail(detail_response))
        job = jobs[0]

        # Test that all fields are present and properly typed
        expected_string_fields = [
            "job_title",
            "job_url",
            "company_name",
            "publication_date",
            "start_date",
            "duration",
            "salary",
            "daily_rate",
            "experience",
            "remote_work",
            "location",
        ]

        expected_list_fields = ["contract_types", "description", "company_description", "skills"]

        for field in expected_string_fields:
            with self.subTest(field=field):
                self.assertIn(field, job)
                self.assertIsInstance(job[field], str)

        for field in expected_list_fields:
            with self.subTest(field=field):
                self.assertIn(field, job)
                self.assertIsInstance(job[field], list)

    def test_icon_mapping_integration(self):
        """Test that icon mapping works correctly in the full parsing context."""
        detail_response = self._create_response("job_detail_full.html")

        jobs = list(self.spider.parse_job_detail(detail_response))
        job = jobs[0]

        # Test specific icon mappings from our fixture
        self.assertEqual(job["start_date"], "01/09/2025")  # Calendar icon
        self.assertEqual(job["duration"], "6 mois")  # Clock icon
        self.assertIn("€⁄an", job["salary"])  # Money icon (salary part)
        self.assertIn("€⁄j", job["daily_rate"])  # Money icon (TJM part)
        self.assertEqual(job["experience"], "5+ years experience")  # Briefcase icon
        self.assertEqual(job["remote_work"], "Télétravail partiel")  # House icon
        self.assertEqual(job["location"], "Paris, France")  # Location icon

    def test_multiple_jobs_processing(self):
        """Test processing multiple job listings."""
        # Create a listing page with multiple jobs
        multi_job_html = """
        <html><body>
            <div class="mb-4 relative">
                <a href="/job1" class="after:absolute after:inset-0">Job 1</a>
            </div>
            <div class="mb-4 relative">
                <a href="/job2" class="after:absolute after:inset-0">Job 2</a>
            </div>
        </body></html>
        """

        response = HtmlResponse(
            url="http://example.com", body=multi_job_html.encode("utf-8"), encoding="utf-8"
        )

        requests = list(self.spider.parse(response))

        # Should generate requests for both jobs
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].url, "http://example.com/job1")
        self.assertEqual(requests[1].url, "http://example.com/job2")

    def test_data_quality_validation(self):
        """Test that extracted data meets quality standards."""
        detail_response = self._create_response("job_detail_full.html")

        jobs = list(self.spider.parse_job_detail(detail_response))
        job = jobs[0]

        # Test data quality constraints
        self.assertTrue(len(job["job_title"]) > 0, "Job title should not be empty")
        self.assertTrue(job["job_url"].startswith("http"), "URL should be valid")

        # Test that lists don't contain empty strings
        self.assertNotIn(
            "", job["contract_types"], "Contract types should not contain empty strings"
        )
        self.assertNotIn("", job["skills"], "Skills should not contain empty strings")

        # Test that salary/TJM are properly formatted if present
        if job["salary"]:
            self.assertIn("€", job["salary"], "Salary should contain currency symbol")
        if job["daily_rate"]:
            self.assertIn("€⁄j", job["daily_rate"], "Daily rate should contain per-day indicator")

    def _assert_complete_job_data(self, job):
        """Helper to assert that a job contains expected complete data."""
        # Required fields
        required_fields = ["job_title", "job_url", "company_name"]
        for field in required_fields:
            self.assertIn(field, job)
            self.assertIsNotNone(job[field])

        # Fields that should be lists
        list_fields = ["contract_types", "description", "company_description", "skills"]
        for field in list_fields:
            self.assertIn(field, job)
            self.assertIsInstance(job[field], list)

        # Sidebar fields (may be empty but should be present)
        sidebar_fields = [
            "start_date",
            "duration",
            "salary",
            "daily_rate",
            "experience",
            "remote_work",
            "location",
        ]
        for field in sidebar_fields:
            self.assertIn(field, job)
            self.assertIsInstance(job[field], str)


if __name__ == "__main__":
    unittest.main()
