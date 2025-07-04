"""
Main DHgate scraper class
"""

import time
import logging
from urllib.parse import urljoin

from ..base_scraper import BaseScraper
from .validator import DHgateValidator
from .extractor import DHgateExtractor
from .utils import DHgateUtils
from .config import DHGATE_CONFIG

logger = logging.getLogger(__name__)


class DHgateScraper(BaseScraper):
    """Main scraper class for DHgate products"""

    def __init__(self):
        super().__init__(
            base_url=DHGATE_CONFIG['base_url'],
            headers=DHGATE_CONFIG['headers']
        )

        self.validator = DHgateValidator()
        self.extractor = DHgateExtractor()
        self.utils = DHgateUtils()

    def scrape_product(self, url):
        """Main scraping function for a DHgate product"""
        try:
            logger.info(f"Scraping DHgate product: {url}")

            response, soup = self.get_page(
                url,
                delay=DHGATE_CONFIG['request_delay'],
                timeout=DHGATE_CONFIG['timeout']
            )

            # Check for 404
            if self.validator.is_404_page(soup, response):
                logger.warning(f"404 page detected for URL: {url}")
                return {'error': '404_page', 'url': url}

            # Check if this is a category page
            if self.validator.is_category_page(soup, url):
                logger.info("Category page detected, getting first product")
                first_product_url = self.utils.get_first_product_url(soup, self.base_url)
                if first_product_url:
                    return self.scrape_product(first_product_url)
                else:
                    return {'error': 'category_page_no_products', 'url': url}

            # Validate it's a proper product page
            if not self.validator.is_valid_product_page(soup):
                logger.warning(f"Invalid product page: {url}")
                return {'error': 'invalid_product_page', 'url': url}

            # Extract all information
            result = {
                'url': url,
                'scraped_at': time.time(),
                'site': 'dhgate',
                'success': True
            }

            # Extract data using the extractor
            result.update(self.extractor.extract_price(soup))
            result.update(self.extractor.extract_availability(soup))
            result.update(self.extractor.extract_product_details(soup))

            # Extract shipping info
            shipping_info = self.extractor.extract_shipping_info(soup)
            if shipping_info:
                result['shipping'] = shipping_info

            logger.info(f"Successfully scraped DHgate product: {result.get('title', 'Unknown')}")
            return result

        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return {'error': 'scraping_failed', 'url': url, 'message': str(e)}