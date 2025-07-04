"""
Data extraction methods for DHgate pages
"""

import re
from .config import DHGATE_CONFIG
from .utils import DHgateUtils


class DHgateExtractor:
    """Handles data extraction from DHgate pages"""

    def __init__(self):
        self.utils = DHgateUtils()

    def extract_price(self, soup):
        """Extract price information from the product page"""
        price_info = {}

        # Try each price selector
        for selector in DHGATE_CONFIG['price_selectors']:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price_value = self.utils.normalize_price(price_text)

                if price_value:
                    price_info.update({
                        'price': price_value,
                        'currency': DHGATE_CONFIG['default_currency'],
                        'original_price_text': price_text
                    })
                    break

        # Look for price ranges or bulk pricing
        price_range_elements = soup.find_all(text=re.compile(r'\$\d+.*-.*\$\d+'))
        if price_range_elements:
            price_info['price_range'] = price_range_elements[0].strip()

        # Look for bulk pricing table
        bulk_prices = self._extract_bulk_pricing(soup)
        if bulk_prices:
            price_info['bulk_pricing'] = bulk_prices

        return price_info

    def _extract_bulk_pricing(self, soup):
        """Extract bulk pricing information"""
        bulk_prices = []

        # Look for quantity-based pricing tables
        price_tables = soup.find_all('table', class_=re.compile(r'price|bulk'))

        for table in price_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    qty_text = cells[0].get_text(strip=True)
                    price_text = cells[1].get_text(strip=True)

                    qty_numbers = self.utils.extract_numbers_from_text(qty_text)
                    price_value = self.utils.normalize_price(price_text)

                    if qty_numbers and price_value:
                        bulk_prices.append({
                            'quantity': qty_numbers[0],
                            'price': price_value,
                            'original_text': f"{qty_text} - {price_text}"
                        })

        return bulk_prices

    def extract_availability(self, soup):
        """Check if the item is available for purchase"""
        availability_info = {
            'available': False,
            'stock_status': 'unknown',
            'stock_quantity': None
        }

        # Check for out of stock indicators
        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in DHGATE_CONFIG['out_of_stock_indicators']):
            availability_info['stock_status'] = 'out_of_stock'
            return availability_info

        # Look for action buttons (add to cart, buy now)
        action_buttons = soup.find_all(
            ['button', 'a'],
            text=re.compile(r'add to cart|buy now|purchase|order now', re.I)
        )

        if action_buttons:
            availability_info['available'] = True
            availability_info['stock_status'] = 'in_stock'

        # Look for stock quantity
        stock_quantity = self._extract_stock_quantity(soup)
        if stock_quantity:
            availability_info['stock_quantity'] = stock_quantity

        return availability_info

    def _extract_stock_quantity(self, soup):
        """Extract stock quantity from page"""
        stock_patterns = [
            r'(\d+)\s*pieces? available',
            r'(\d+)\s*in stock',
            r'stock:\s*(\d+)',
            r'quantity:\s*(\d+)'
        ]

        page_text = soup.get_text()

        for pattern in stock_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                return int(match.group(1))

        return None

    def extract_shipping_info(self, soup):
        """Extract shipping information"""
        shipping_info = {}

        # Look for free shipping
        if soup.find(text=re.compile(r'free shipping', re.I)):
            shipping_info['shipping_cost'] = 0.0
            shipping_info['free_shipping'] = True
        else:
            # Look for shipping cost
            shipping_cost = self._extract_shipping_cost(soup)
            if shipping_cost:
                shipping_info['shipping_cost'] = shipping_cost

        # Look for delivery time
        delivery_time = self._extract_delivery_time(soup)
        if delivery_time:
            shipping_info['delivery_time'] = delivery_time

        # Look for shipping methods
        shipping_methods = self._extract_shipping_methods(soup)
        if shipping_methods:
            shipping_info['shipping_methods'] = shipping_methods

        return shipping_info

    def _extract_shipping_cost(self, soup):
        """Extract shipping cost"""
        shipping_elements = soup.find_all(text=re.compile(r'shipping.*\$\d+', re.I))

        for element in shipping_elements:
            cost_match = re.search(r'\$(\d+\.?\d*)', element)
            if cost_match:
                return float(cost_match.group(1))

        return None

    def _extract_delivery_time(self, soup):
        """Extract delivery time information"""
        delivery_patterns = [
            r'(\d+)-(\d+)\s*days?',
            r'delivery.*?(\d+)\s*days?',
            r'(\d+)\s*business days?'
        ]

        page_text = soup.get_text()

        for pattern in delivery_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                if len(match.groups()) >= 2:
                    return f"{match.group(1)}-{match.group(2)} days"
                else:
                    return f"{match.group(1)} days"

        return None

    def _extract_shipping_methods(self, soup):
        """Extract available shipping methods"""
        methods = []

        # Common shipping method keywords
        method_keywords = [
            'dhl', 'fedex', 'ups', 'usps', 'ems', 'china post',
            'standard shipping', 'express shipping', 'economy shipping'
        ]

        page_text = soup.get_text().lower()

        for keyword in method_keywords:
            if keyword in page_text:
                methods.append(keyword.title())

        return methods

    def extract_product_details(self, soup):
        """Extract additional product details"""
        details = {}

        # Product title
        title = self._extract_title(soup)
        if title:
            details['title'] = title

        # Seller information
        seller = self._extract_seller_info(soup)
        if seller:
            details['seller'] = seller

        # Rating and reviews
        rating_info = self._extract_rating_info(soup)
        details.update(rating_info)

        # Product images
        images = self._extract_product_images(soup)
        if images:
            details['images'] = images

        # Product specifications
        specs = self._extract_specifications(soup)
        if specs:
            details['specifications'] = specs

        return details

    def _extract_title(self, soup):
        """Extract product title"""
        for selector in DHGATE_CONFIG['title_selectors']:
            title_element = soup.select_one(selector)
            if title_element:
                return self.utils.clean_text(title_element.get_text(strip=True))
        return None

    def _extract_seller_info(self, soup):
        """Extract seller information"""
        seller_selectors = [
            '.seller-name',
            '.store-name',
            '[data-testid="seller-name"]'
        ]

        for selector in seller_selectors:
            seller_element = soup.select_one(selector)
            if seller_element:
                return self.utils.clean_text(seller_element.get_text(strip=True))

        # Fallback: look for text containing "seller" or "store"
        seller_elements = soup.find_all(['a', 'span'], text=re.compile(r'seller|store', re.I))
        if seller_elements:
            return self.utils.clean_text(seller_elements[0].get_text(strip=True))

        return None

    def _extract_rating_info(self, soup):
        """Extract rating and review information"""
        rating_info = {}

        # Look for rating (stars)
        rating_elements = soup.find_all(['span', 'div'], class_=re.compile(r'rating|star|review'))
        for element in rating_elements:
            rating_text = element.get_text(strip=True)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                rating_info['rating'] = float(rating_match.group(1))
                break

        # Look for number of reviews
        review_elements = soup.find_all(text=re.compile(r'(\d+)\s*reviews?', re.I))
        for review_text in review_elements:
            review_match = re.search(r'(\d+)', review_text)
            if review_match:
                rating_info['review_count'] = int(review_match.group(1))
                break

        return rating_info

    def _extract_product_images(self, soup):
        """Extract product image URLs"""
        images = []

        # Common image selectors
        image_selectors = [
            '.product-image img',
            '.gallery img',
            '.image-gallery img',
            '.product-photos img',
            '.main-image img'
        ]

        for selector in image_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-original')
                if src and src not in images:
                    images.append(src)

        return images

    def _extract_specifications(self, soup):
        """Extract product specifications"""
        specs = {}

        # Look for specification tables
        spec_tables = soup.find_all('table', class_=re.compile(r'spec|detail|attribute'))

        for table in spec_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = self.utils.clean_text(cells[0].get_text(strip=True))
                    value = self.utils.clean_text(cells[1].get_text(strip=True))
                    if key and value:
                        specs[key] = value

        return specs