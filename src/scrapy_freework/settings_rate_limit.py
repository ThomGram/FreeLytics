# Scrapy settings for handling rate limiting and 429 errors
# This file contains conservative settings to avoid being rate limited

# Basic rate limiting settings
DOWNLOAD_DELAY = 0.5  # 2 seconds delay between requests
RANDOMIZE_DOWNLOAD_DELAY = 0.5  # Randomize delay (1.5 to 2.5 seconds)
CONCURRENT_REQUESTS = 1  # Only 1 concurrent request
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Retry settings for handling 429 and other errors
RETRY_TIMES = 5  # Retry failed requests up to 5 times
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 408, 522, 524, 408, 418]
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 1, 2, 4, 8, 16 seconds

# AutoThrottle extension for adaptive rate limiting
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 60  # Maximum delay of 60 seconds
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = True  # Enable to see throttling stats in logs

# User agent to appear more like a regular browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Additional headers to appear more browser-like
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Enable cookies to maintain session state
COOKIES_ENABLED = True

# Log level for debugging rate limiting issues
LOG_LEVEL = "INFO"
