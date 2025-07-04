"""
Enhanced configuration settings for DHgate scraper with bypass strategies
"""

DHGATE_CONFIG = {
    # Base settings
    'base_url': 'https://www.dhgate.com',
    'default_currency': 'USD',

    # Request settings with enhanced headers
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Cache-Control': 'max-age=0',
    },

    # Enhanced timing settings
    'request_delay': 3,  # Minimum seconds between requests
    'batch_delay': 5,    # seconds between batch requests
    'timeout': 30,       # request timeout in seconds
    'max_retries': 2,    # maximum retry attempts
    'retry_delay': 10,   # seconds between retries

    # Alternative domains to try
    'alternative_domains': [
        'https://www.dhgate.com',
        'https://m.dhgate.com',
        'https://dhgate.com',
    ],

    # Mobile headers for mobile site access
    'mobile_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    },

    # CSS Selectors (expanded)
    'price_selectors': [
        '.price-now',
        '.price-current',
        '.product-price',
        '.price',
        '[data-testid="price"]',
        '.pricenow',
        '.now-price',
        '.unit-price',
        '.current-price',
        '.sale-price',
        '.final-price'
    ],

    'title_selectors': [
        'h1',
        '.product-title',
        '.title',
        '[data-testid="product-title"]',
        '.product-name',
        '.item-title',
        '.goods-title',
        '.product-info h1'
    ],

    'seller_selectors': [
        '.seller-name',
        '.store-name',
        '[data-testid="seller-name"]',
        '.shop-name',
        '.supplier-name'
    ],

    'image_selectors': [
        '.product-image img',
        '.gallery img',
        '.image-gallery img',
        '.product-photos img',
        '.main-image img',
        '.goods-image img'
    ],

    # Error indicators
    'error_indicators': [
        'page not found',
        'error 404',
        'page does not exist',
        'sorry, the page you are looking for',
        'product not found',
        'item not found',
        'access denied',
        'blocked',
        'temporarily unavailable'
    ],

    # Stock indicators
    'out_of_stock_indicators': [
        'out of stock',
        'sold out',
        'not available',
        'unavailable',
        'temporarily unavailable',
        'stock: 0',
        'quantity: 0',
        'discontinued'
    ],

    # Connection test settings
    'connection_test_timeout': 20,
    'connection_test_urls': [
        'https://www.dhgate.com/robots.txt',
        'https://m.dhgate.com',
        'https://www.dhgate.com'
    ],

    # Search settings
    'search_variations': {
        'add_wholesale': True,
        'try_single_words': True,
        'remove_brand_names': True,
        'fallback_generic': True
    },

    # Quality thresholds
    'min_title_length': 10,
    'max_title_length': 200,
    'min_price': 0.01,
    'max_price': 10000,

    # Data validation
    'required_fields': ['title', 'price', 'available'],
    'optional_fields': ['seller', 'rating', 'review_count', 'shipping', 'images']
}

# Alternative wholesale sites if DHgate fails
ALTERNATIVE_WHOLESALE_SITES = {
    'alibaba': {
        'base_url': 'https://www.alibaba.com',
        'search_url': 'https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={search_term}',
        'selectors': {
            'product_links': '.item-info a',
            'title': '.item-title',
            'price': '.price'
        }
    },
    'aliexpress': {
        'base_url': 'https://www.aliexpress.com',
        'search_url': 'https://www.aliexpress.com/wholesale?SearchText={search_term}',
        'selectors': {
            'product_links': '.product-item a',
            'title': '.item-title',
            'price': '.price-current'
        }
    },
    'globalsources': {
        'base_url': 'https://www.globalsources.com',
        'search_url': 'https://www.globalsources.com/gsol/I/s/{search_term}',
        'selectors': {
            'product_links': '.product-item a',
            'title': '.product-title',
            'price': '.price'
        }
    }
}