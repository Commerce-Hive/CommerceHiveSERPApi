"""
Base scraper class with common functionality
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.session = requests.Session()

        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        if headers:
            default_headers.update(headers)

        self.session.headers.update(default_headers)

    def get_page(self, url, delay=1, timeout=10):
        """Get a page with error handling"""
        try:
            time.sleep(delay)
            response = self.session.get(url, timeout=timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            return response, soup
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise

    @abstractmethod
    def scrape_product(self, url):
        """Abstract method to scrape a single product"""
        pass

    def scrape_multiple_products(self, urls, delay=2):
        """Scrape multiple products with delay"""
        results = []

        for url in urls:
            try:
                result = self.scrape_product(url)
                results.append(result)
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                results.append({
                    'error': 'scraping_failed',
                    'url': url,
                    'message': str(e)
                })

        return results