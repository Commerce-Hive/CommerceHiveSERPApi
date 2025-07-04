"""
Utility functions for DHgate scraping
"""

import re
from urllib.parse import urljoin


class DHgateUtils:
    """Utility functions for DHgate scraping"""

    def get_first_product_url(self, soup, base_url):
        """Get the URL of the first product from a category page"""
        # Look for product links
        product_links = soup.find_all('a', href=re.compile(r'/product/'))
        if product_links:
            first_link = product_links[0]['href']
            if first_link.startswith('/'):
                return urljoin(base_url, first_link)
            return first_link
        return None

    def clean_text(self, text):
        """Clean extracted text"""
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        # Remove problematic characters
        text = re.sub(r'[^\w\s\-\.\,\$\%\(\)\[\]/]', '', text)
        return text.strip()

    def normalize_price(self, price_text):
        """Normalize price text to extract numeric value"""
        if not price_text:
            return None

        # Remove currency symbols and extra characters
        cleaned = re.sub(r'[^\d\.\,]', '', price_text)
        # Handle comma as thousands separator
        cleaned = cleaned.replace(',', '')

        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def extract_numbers_from_text(self, text, pattern=None):
        """Extract numbers from text using optional pattern"""
        if not text:
            return []

        if pattern:
            matches = re.findall(pattern, text)
        else:
            matches = re.findall(r'\d+\.?\d*', text)

        numbers = []
        for match in matches:
            try:
                if '.' in str(match):
                    numbers.append(float(match))
                else:
                    numbers.append(int(match))
            except (ValueError, TypeError):
                continue

        return numbers

    def is_valid_dhgate_url(self, url):
        """Check if URL is valid DHgate URL"""
        if not url:
            return False

        valid_patterns = [
            r'dhgate\.com',
            r'/product/',
            r'/store/'
        ]

        return any(re.search(pattern, url, re.I) for pattern in valid_patterns)

    def format_shipping_time(self, time_text):
        """Format shipping time text consistently"""
        if not time_text:
            return None

        # Extract numbers and format consistently
        numbers = self.extract_numbers_from_text(time_text)
        if len(numbers) == 1:
            return f"{int(numbers[0])} days"
        elif len(numbers) >= 2:
            return f"{int(numbers[0])}-{int(numbers[1])} days"

        return time_text

    def extract_currency_from_text(self, text):
        """Extract currency symbol from price text"""
        if not text:
            return None

        currency_symbols = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR'
        }

        for symbol, currency in currency_symbols.items():
            if symbol in text:
                return currency

        return 'USD'  # Default to USD

    def validate_extracted_data(self, data):
        """Validate extracted data for completeness"""
        required_fields = ['title', 'price', 'available']
        missing_fields = []

        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        return {
            'is_valid': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'completeness_score': (len(required_fields) - len(missing_fields)) / len(required_fields)
        }