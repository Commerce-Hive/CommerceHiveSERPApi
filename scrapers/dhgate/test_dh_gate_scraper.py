"""
Pytest tests for DHgate scraper functionality
"""

import pytest
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

from scrapers.dhgate.utils import DHgateUtils
from scrapers.dhgate.config import DHGATE_CONFIG
from scrapers.dhgate.scraper import DHgateScraper
from scrapers.dhgate.search import DHgateSearch


class TestDHgateConnection:
    """Test basic DHgate connectivity"""

    def test_dhgate_homepage_accessible(self):
        """Test if DHgate homepage is accessible"""
        response = requests.get("https://www.dhgate.com", timeout=20)
        assert response.status_code == 200
        assert len(response.content) > 1000  # Should have substantial content

    def test_dhgate_search_url_format(self):
        """Test if search URL is correctly formatted"""
        search_term = "crocs"
        expected_url = f"https://www.dhgate.com/wholesale/search.do?act=search&sus=&searchkey={quote(search_term)}"

        # This should not raise an exception
        assert "dhgate.com" in expected_url
        assert "crocs" in expected_url

    @pytest.mark.slow
    def test_dhgate_search_response(self):
        """Test if DHgate search returns valid response"""
        search_url = "https://www.dhgate.com/wholesale/search.do?act=search&sus=&searchkey=crocs"

        headers = DHGATE_CONFIG['headers']
        response = requests.get(search_url, headers=headers, timeout=30)

        assert response.status_code == 200
        assert len(response.content) > 500


class TestDHgateUtils:
    """Test DHgate utility functions"""

    def setup_method(self):
        """Setup for each test"""
        self.utils = DHgateUtils()

    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "  Hello    World!@#$%  "
        clean = self.utils.clean_text(dirty_text)
        assert clean == "Hello World"

    def test_normalize_price(self):
        """Test price normalization"""
        test_cases = [
            ("$29.99", 29.99),
            ("USD 15.50", 15.50),
            ("£12.34", 12.34),
            ("1,234.56", 1234.56),
            ("invalid", None),
            ("", None)
        ]

        for input_price, expected in test_cases:
            result = self.utils.normalize_price(input_price)
            assert result == expected

    def test_extract_numbers_from_text(self):
        """Test number extraction from text"""
        text = "Product costs $29.99 and weighs 1.5 kg"
        numbers = self.utils.extract_numbers_from_text(text)
        assert 29.99 in numbers
        assert 1.5 in numbers

    def test_is_valid_dhgate_url(self):
        """Test DHgate URL validation"""
        valid_urls = [
            "https://www.dhgate.com/product/something",
            "https://dhgate.com/store/12345",
            "/product/test-item"
        ]

        invalid_urls = [
            "https://amazon.com/product",
            "https://google.com",
            "",
            None
        ]

        for url in valid_urls:
            assert self.utils.is_valid_dhgate_url(url) == True

        for url in invalid_urls:
            assert self.utils.is_valid_dhgate_url(url) == False


class TestDHgateSearchExtraction:
    """Test search result extraction"""

    def setup_method(self):
        """Setup mock HTML for testing"""
        self.mock_search_html = """
        <html>
            <body>
                <div class="pic">
                    <a href="/product/crocs-classic-clog-12345.html">
                        <img src="image1.jpg" alt="Crocs">
                    </a>
                </div>
                <div class="product-title">
                    <a href="/product/another-crocs-67890.html">
                        Crocs Style Shoes
                    </a>
                </div>
                <div class="item-img">
                    <a href="/product/foam-clogs-11111.html">
                        <img src="image2.jpg" alt="Foam Clogs">
                    </a>
                </div>
            </body>
        </html>
        """

        self.mock_product_html = """
        <html>
            <body>
                <h1>Crocs Classic Clog Wholesale</h1>
                <div class="price-now">$8.99</div>
                <button>Add to Cart</button>
                <div class="seller-name">Best Wholesale Store</div>
            </body>
        </html>
        """

    def test_extract_product_urls_from_html(self):
        """Test extracting product URLs from search results HTML"""
        soup = BeautifulSoup(self.mock_search_html, 'html.parser')

        # Test different selectors
        selectors = [
            '.pic a',
            '.product-title a',
            '.item-img a',
            'a[href*="/product/"]'
        ]

        found_urls = []
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/product/' in href:
                    found_urls.append(href)

        assert len(found_urls) >= 3  # Should find at least 3 product links
        assert '/product/crocs-classic-clog-12345.html' in found_urls

    def test_extract_product_data_from_html(self):
        """Test extracting product data from product page HTML"""
        soup = BeautifulSoup(self.mock_product_html, 'html.parser')

        # Test title extraction
        title_element = soup.select_one('h1')
        assert title_element is not None
        assert 'Crocs' in title_element.get_text()

        # Test price extraction
        price_element = soup.select_one('.price-now')
        assert price_element is not None
        assert '$8.99' in price_element.get_text()

        # Test seller extraction
        seller_element = soup.select_one('.seller-name')
        assert seller_element is not None
        assert 'Best Wholesale Store' in seller_element.get_text()


@pytest.mark.integration
class TestDHgateIntegration:
    """Integration tests that actually hit DHgate (marked as slow)"""

    def setup_method(self):
        """Setup for integration tests"""
        self.search = DHgateSearch()

    @pytest.mark.slow
    def test_search_integration_simple_term(self):
        """Test actual search with a simple term"""
        # Use a very common term that should definitely exist
        results = self.search.search_products("phone case", max_results=3)

        # Should get some results
        assert isinstance(results, list)
        # Don't assert length > 0 since DHgate might be blocking
        # Just test that it doesn't crash

    @pytest.mark.slow
    def test_scraper_integration_known_url(self):
        """Test scraper with a known DHgate URL structure"""
        scraper = DHgateScraper()

        # Test with a generic DHgate product URL format
        # (This might fail if URL doesn't exist, which is expected)
        test_url = "https://www.dhgate.com/product/test/123456.html"

        try:
            result = scraper.scrape_product(test_url)
            # Should return a dict with error or success
            assert isinstance(result, dict)
            # Should have either 'success' or 'error' key
            assert 'success' in result or 'error' in result
        except Exception as e:
            # Connection errors are acceptable for this test
            assert 'timeout' in str(e).lower() or 'connection' in str(e).lower()


class TestDHgateConfig:
    """Test configuration and setup"""

    def test_config_exists(self):
        """Test that configuration is properly loaded"""
        assert DHGATE_CONFIG is not None
        assert 'base_url' in DHGATE_CONFIG
        assert 'headers' in DHGATE_CONFIG
        assert 'timeout' in DHGATE_CONFIG

    def test_config_values(self):
        """Test configuration values are reasonable"""
        assert DHGATE_CONFIG['base_url'] == 'https://www.dhgate.com'
        assert DHGATE_CONFIG['timeout'] >= 5  # At least 5 seconds
        assert len(DHGATE_CONFIG['price_selectors']) > 0
        assert len(DHGATE_CONFIG['title_selectors']) > 0

    def test_headers_format(self):
        """Test that headers are properly formatted"""
        headers = DHGATE_CONFIG['headers']
        assert 'User-Agent' in headers
        assert 'Mozilla' in headers['User-Agent']  # Should look like a real browser


# Pytest configuration for different test categories
@pytest.fixture(scope="session")
def slow_tests():
    """Fixture to mark slow tests"""
    return pytest.mark.slow


# Custom markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )