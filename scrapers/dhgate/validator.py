"""
Validation logic for DHgate pages
"""

import re
from .config import DHGATE_CONFIG


class DHgateValidator:
    """Handles validation logic for DHgate pages"""

    def is_404_page(self, soup, response):
        """Check if the page is a 404 error page"""
        if response.status_code == 404:
            return True

        page_text = soup.get_text().lower()
        return any(
            indicator in page_text
            for indicator in DHGATE_CONFIG['error_indicators']
        )

    def is_category_page(self, soup, url):
        """Check if this is a category page instead of a product page"""
        # DHgate product URLs typically contain '/product/' or '/store/'
        if '/product/' not in url and '/store/' not in url:
            return True

        # Check for multiple product listings
        product_items = soup.find_all(['div', 'li'], class_=re.compile(r'product|item'))
        if len(product_items) > 5:  # If many products, likely a category
            return True

        return False

    def is_valid_product_page(self, soup):
        """Check if this is a valid product page with essential elements"""
        # Must have a title
        has_title = any(
            soup.select_one(selector)
            for selector in DHGATE_CONFIG['title_selectors']
        )

        # Must have some form of price
        has_price = any(
            soup.select_one(selector)
            for selector in DHGATE_CONFIG['price_selectors']
        )

        return has_title and has_price

    def is_product_available(self, soup):
        """Basic availability check"""
        page_text = soup.get_text().lower()
        return not any(
            indicator in page_text
            for indicator in DHGATE_CONFIG['out_of_stock_indicators']
        )

    def has_bulk_pricing(self, soup):
        """Check if product has bulk pricing options"""
        bulk_indicators = [
            'bulk price',
            'wholesale',
            'quantity discount',
            'piece price'
        ]

        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in bulk_indicators)

    def is_contact_seller_page(self, soup):
        """Check if this requires contacting seller (not direct purchase)"""
        contact_indicators = [
            'contact seller',
            'email for price',
            'request quote',
            'inquiry'
        ]

        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in contact_indicators)