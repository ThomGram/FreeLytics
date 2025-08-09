# Makefile for FreeworkSpider project using UV

.PHONY: test test-unit test-integration test-coverage clean lint format install sync

# Development setup
install:
	cd ../../ && uv sync --extra test --extra dev

sync:
	cd ../../ && uv sync

# Test commands (run from project root)
test:
	cd ../../ && uv run pytest scraper/scrapy_freework/tests/ -v

test-unit:
	cd ../../ && uv run pytest scraper/scrapy_freework/tests/test_config.py scraper/scrapy_freework/tests/test_parsing.py scraper/scrapy_freework/tests/test_data_processing.py -v -m "not integration"

test-integration:
	cd ../../ && uv run pytest scraper/scrapy_freework/tests/test_integration.py -v -m integration

test-coverage:
	cd ../../ && uv run pytest scraper/scrapy_freework/tests/ --cov=scraper/scrapy_freework --cov-report=html --cov-report=term-missing

# Code quality
lint:
	cd ../../ && uv run flake8 scraper/scrapy_freework/ --max-line-length=100 --ignore=E203,W503
	cd ../../ && uv run mypy scraper/scrapy_freework/ --ignore-missing-imports

format:
	cd ../../ && uv run black scraper/scrapy_freework/ --line-length=100
	cd ../../ && uv run isort scraper/scrapy_freework/ --line-length=100

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

# Run scraper
scrape:
	cd ../../ && uv run scrapy crawl freework -s LOG_LEVEL=INFO

scrape-debug:
	cd ../../ && uv run scrapy crawl freework -s LOG_LEVEL=DEBUG

# Check UV environment
env-info:
	cd ../../ && uv pip list

# Help
help:
	@echo "UV-based FreeworkSpider Commands:"
	@echo "  install         - Install all dependencies with uv sync"
	@echo "  sync            - Sync dependencies"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  lint            - Run code linting"
	@echo "  format          - Format code with black and isort"
	@echo "  clean           - Clean up generated files"
	@echo "  scrape          - Run the scraper"
	@echo "  scrape-debug    - Run the scraper with debug logging"
	@echo "  env-info        - Show installed packages"
