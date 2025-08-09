# FreeworkSpider

A Scrapy spider for scraping job listings from Free-Work.com using UV for dependency management.

## Setup with UV

### 1. Install Dependencies
```bash
# From the scrapy_freework directory
make install

# Or manually from project root
cd ../../
uv sync --extra test --extra dev
```

### 2. Run Tests
```bash
# All tests
make test

# Unit tests only (fast)
make test-unit

# Integration tests only
make test-integration

# With coverage
make test-coverage
```

### 3. Direct UV Commands

From the project root (`/home/toto/Documents/Grammaticorp/FreeLytics/`):

```bash
# Install dependencies
uv sync --extra test --extra dev

# Run unit tests
uv run pytest scrapy_freework/tests/test_config.py scrapy_freework/tests/test_parsing.py scrapy_freework/tests/test_data_processing.py -v

# Run all tests
uv run pytest scrapy_freework/tests/ -v

# Run the spider
uv run scrapy crawl freework -s LOG_LEVEL=INFO

# Check environment
uv pip list
```

### 4. Development Commands
```bash
# Format code
make format

# Lint code
make lint

# Clean up
make clean
```

## Project Structure

```
scrapy_freework/
├── scrapy_freework/
│   ├── spiders/
│   │   └── freework_spider.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   └── __init__.py
├── tests/
│   ├── fixtures/
│   │   ├── test_config.cfg
│   │   ├── job_listing_page.html
│   │   └── job_detail_full.html
│   ├── test_config.py
│   ├── test_parsing.py
│   ├── test_data_processing.py
│   ├── test_integration.py
│   └── conftest.py
├── Makefile
└── README.md
```

## Configuration

Create a `FreeLytics.cfg` file in the project root with:

```ini
[freework]
jobs = ["data scientist", "machine learning"]
locations = ["fr~~~", "paris"]
contracts = ["permanent", "freelance"]
base_url = https://www.free-work.com/fr/tech-it/jobs?query=
```

## Testing Philosophy

The test suite uses **real HTML fixtures** instead of mocks for:
- Faster, more reliable tests
- Better detection of HTML structure changes
- Easier maintenance when the site updates
- CI-ready with no external dependencies

## UV Benefits

- **Fast dependency resolution** - UV is much faster than pip
- **Lockfile support** - Ensures reproducible installs
- **Virtual environment management** - Automatic venv handling
- **Modern Python packaging** - Uses pyproject.toml instead of requirements.txt
