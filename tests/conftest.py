"""
pytest configuration file for FreeworkSpider tests.
This file contains fixtures and configuration shared across all tests.
"""

import sys
from pathlib import Path

import pytest

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent))


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_config_path(fixtures_dir):
    """Return path to sample config file."""
    return fixtures_dir / "test_config.cfg"


@pytest.fixture
def job_listing_html(fixtures_dir):
    """Return job listing HTML content."""
    with open(fixtures_dir / "job_listing_page.html", "r") as f:
        return f.read()


@pytest.fixture
def job_detail_html(fixtures_dir):
    """Return job detail HTML content."""
    with open(fixtures_dir / "job_detail_full.html", "r") as f:
        return f.read()
