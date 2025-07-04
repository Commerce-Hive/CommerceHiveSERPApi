"""
Enhanced DHgate search with bypass strategies
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import time
import random
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import DHGATE_CONFIG
from .scraper import DHgateScraper
from .utils import DHgateUtils


class DHgateBypassSession:
    """Handles bypass strategies for DHgate access"""

    def __init__(self):
        self.session = None
        self.last_request_time = 0
        self.min_delay = 3

    def create_stealth_session(self):
        """Create a session designed to avoid detection"""
        session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Realistic browser headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })

        self.session = session
        return session

    def respect_rate_limits(self):
        """Ensure proper delays between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last + random.uniform(0.5, 2.0)
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def safe_request(self, url, timeout=30):
        """Make a safe request with multiple fallback strategies"""
        strategies = [
            self._try_standard_request,
            self._try_mobile_site,
            self._try_session_buildup,
        ]

        for strategy in strategies:
            try:
                self.respect_rate_limits()
                response = strategy(url, timeout)
                if response and response.status_code == 200:
                    return response
            except Exception as e:
                print(f"Strategy failed: {strategy.__name__} - {type(e).__name__}")
                continue

        return None

    def _try_standard_request(self, url, timeout):
        """Standard request with good headers"""
        headers = DHGATE_CONFIG['headers'].copy()
        return requests.get(url, headers=headers, timeout=timeout)

    def _try_mobile_site(self, url, timeout):
        """Try mobile version of DHgate"""
        mobile_url = url.replace('www.dhgate.com', 'm.dhgate.com')
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        return requests.get(mobile_url, headers=mobile_headers, timeout=timeout)

    def _try_session_buildup(self, url, timeout):
        """Try building session gradually"""
        if not self.session:
            self.create_stealth_session()

        # First visit robots.txt
        try:
            robots_url = "https://www.dhgate.com/robots.txt"
            self.session.get(robots_url, timeout=15)
            time.sleep(1)
        except:
            pass

        return self.session.get(url, timeout=timeout)


class DHgateSearch:
    """Enhanced search with bypass capabilities"""

    def __init__(self):
        self.base_url = DHGATE_CONFIG['base_url']
        self.scraper = DHgateScraper()
        self.utils = DHgateUtils()
        self.bypass = DHgateBypassSession()

    def search_products(self, search_term, max_results=10):
        """Search DHgate with enhanced bypass strategies"""
        print(f"🔍 Searching DHgate for: '{search_term}'")

        # Clean the search term
        clean_term = self._clean_search_term(search_term)

        # Try multiple search variations
        search_variations = self._generate_search_variations(clean_term)

        for i, variation in enumerate(search_variations):
            print(f"🔍 Search variation {i + 1}: '{variation}'")

            try:
                results = self._search_single_term(variation, max_results)
                if results:
                    print(f"✅ Found {len(results)} results with variation: '{variation}'")
                    return results
                else:
                    print(f"❌ No results for variation: '{variation}'")
            except Exception as e:
                print(f"Search failed: {e}")
                continue

            # Add delay between search variations
            time.sleep(2)

        print("❌ All search variations failed")
        return []

    def _search_single_term(self, search_term, max_results):
        """Search for a single term with bypass strategies"""
        # Build search URL
        search_url = f"{self.base_url}/wholesale/search.do?act=search&sus=&searchkey={quote(search_term)}"

        print(f"🌐 Trying URL: {search_url}")

        # Use bypass session to get search results
        response = self.bypass.safe_request(search_url)

        if not response:
            raise Exception("Could not access DHgate search")

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product URLs
        product_urls = self._extract_product_urls(soup, max_results)

        if not product_urls:
            print("⚠️  No product URLs found in search results")
            return []

        print(f"📦 Found {len(product_urls)} product URLs")

        # Scrape each product with delays
        results = []
        for i, url in enumerate(product_urls[:max_results]):
            try:
                print(f"📄 Scraping product {i+1}/{len(product_urls)}: {url}")
                product_data = self.scraper.scrape_product(url)

                if product_data.get('success'):
                    results.append(product_data)
                    print(f"✅ Successfully scraped: {product_data.get('title', 'Unknown')[:50]}...")
                else:
                    print(f"❌ Failed to scrape product: {product_data.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")
                continue

            # Important: Add delay between product scrapes
            if i < len(product_urls) - 1:
                time.sleep(3)

        return results

    def _generate_search_variations(self, search_term):
        """Generate different search term variations"""
        variations = [search_term]

        # Add "wholesale" to search
        if 'wholesale' not in search_term.lower():
            variations.append(f"{search_term} wholesale")

        # Try just the main product category
        words = search_term.split()
        if len(words) > 1:
            # Try first word only
            variations.append(words[0])
            # Try last word only
            variations.append(words[-1])

        # Generic fallback
        variations.append("wholesale")

        return variations

    def _clean_search_term(self, term):
        """Enhanced search term cleaning"""
        # Remove Amazon-specific terms
        amazon_terms = ['amazon', 'prime', 'eligible', 'asin:', 'brand:', 'essentials']

        for amazon_term in amazon_terms:
            term = re.sub(amazon_term, '', term, flags=re.IGNORECASE)

        # Remove extra whitespace and special characters
        term = re.sub(r'\s+', ' ', term).strip()
        term = re.sub(r'[^\w\s-]', '', term)

        # Remove common unhelpful words
        stop_words = ['the', 'and', 'or', 'with', 'for', 'in', 'on', 'at']
        words = term.split()
        words = [w for w in words if w.lower() not in stop_words]

        return ' '.join(words)

    def _extract_product_urls(self, soup, max_results):
        """Enhanced product URL extraction"""
        urls = []

        # Multiple selectors to try
        selectors = [
            'a[href*="/product/"]',
            '.pic a',
            '.product-title a',
            '.item-img a',
            '.product-item a',
            '.goods-item a'
        ]

        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/product/' in href:
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    if href not in urls and self.utils.is_valid_dhgate_url(href):
                        urls.append(href)

                    if len(urls) >= max_results:
                        break

            if len(urls) >= max_results:
                break

        return urls

    def test_connection(self):
        """Test DHgate connectivity with various methods"""
        print("🧪 Testing DHgate connection...")

        test_urls = [
            "https://www.dhgate.com",
            "https://m.dhgate.com",
            "https://dhgate.com"
        ]

        for url in test_urls:
            try:
                response = self.bypass.safe_request(url)
                if response:
                    print(f"✅ {url} - Status: {response.status_code}, Size: {len(response.content)}")
                    return True
                else:
                    print(f"❌ {url} - Failed")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")

        print("❌ All connection tests failed")
        return False