import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re

SERPAPI_API_KEY = "93f92def6771bede4c8f3b29b7a898e21bf2289ec589dc8ba905f760230a4c62"
print("API Key:", SERPAPI_API_KEY)


def clean_product_name_for_search(full_amazon_title):
    """Clean Amazon product title to search for alternatives"""
    title = re.sub(r'\(ASIN:.*?\)', '', full_amazon_title).strip()

    title = re.sub(r'- (Amazon|Prime|Eligible)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'Amazon\.com', '', title, flags=re.IGNORECASE)

    title = re.sub(r'\s*[-,]\s*$', '', title).strip() # use regex to find the white spaces

    parts = title.split(' - ')
    if len(parts) > 1:
        core_name = parts[0]
        # Keep important descriptive parts
        for part in parts[1:]:
            if any(keyword in part.lower() for keyword in
                   ['wireless', 'bluetooth', 'usb', 'black', 'white', 'size', 'gb', 'tb', 'inch']):
                core_name += ' ' + part
                break
        title = core_name

    return title.strip()


def find_alternatives_to_amazon_product(amazon_product_title, amazon_price=None):
    """Find alternatives to an Amazon product, including Amazon if it's cheapest"""

    # Clean the product name
    clean_name = clean_product_name_for_search(amazon_product_title)
    print(f"🎯 Cleaned search term: {clean_name}")

    # Search ALL sites including Amazon
    results = run_wholesaler_scraper(clean_name)

    # Separate Amazon and non-Amazon results
    amazon_results = []
    competitor_results = []

    for result in results:
        if 'amazon.com' in result.get('wholesaler', '').lower():
            amazon_results.append(result)
        else:
            competitor_results.append(result)

    # If we have the original Amazon price, add it to comparison
    if amazon_price and amazon_price != 'N/A':
        amazon_results.append({
            "wholesaler": "amazon.com",
            "store": "amazon.com",
            "title": amazon_product_title,
            "price": f"${amazon_price}",
            "product_url": "#",
            "availability": "Available"
        })

    # Combine all results for price comparison
    all_results = amazon_results + competitor_results

    # Try to extract numeric prices for comparison
    results_with_prices = []
    for result in all_results:
        price_text = result.get('price', 'Check site')
        numeric_price = extract_numeric_price(price_text)
        result['numeric_price'] = numeric_price
        if numeric_price is not None:
            results_with_prices.append(result)

    # Sort by price (lowest first)
    results_with_prices.sort(key=lambda x: x['numeric_price'])

    # Add results without prices at the end
    results_without_prices = [r for r in all_results if r['numeric_price'] is None]

    final_results = results_with_prices + results_without_prices

    # Mark the cheapest option
    if results_with_prices:
        cheapest_price = results_with_prices[0]['numeric_price']
        for result in final_results:
            if result.get('numeric_price') == cheapest_price:
                result['is_cheapest'] = True
            else:
                result['is_cheapest'] = False

    return final_results


def extract_numeric_price(price_text):
    """Extract numeric price from price string"""
    if not price_text or price_text in ['Check site', 'N/A']:
        return None

    import re
    # Remove currency symbols and extract numbers
    price_match = re.search(r'[\d,]+\.?\d*', str(price_text).replace(',', ''))
    if price_match:
        try:
            return float(price_match.group())
        except ValueError:
            return None
    return None


def display_price_comparison(results, original_amazon_title):
    """Display results with price comparison highlighting"""
    print(f"\n🛒 Price Comparison for: {original_amazon_title}")
    print("=" * 80)

    if not results:
        print("❌ No results found")
        return

    cheapest_found = False
    amazon_is_cheapest = False

    for i, result in enumerate(results, 1):
        store = result.get('store', 'Unknown')
        title = result.get('title', 'No title')
        price = result.get('price', 'Check site')
        availability = result.get('availability', 'Unknown')
        is_cheapest = result.get('is_cheapest', False)

        # Check if this is Amazon and it's cheapest
        if 'amazon.com' in store.lower() and is_cheapest:
            amazon_is_cheapest = True

        # Format the display
        cheapest_indicator = " 🏆 CHEAPEST!" if is_cheapest else ""
        store_display = store.upper()

        print(f"{i}. {store_display}{cheapest_indicator}")
        print(f"   Price: {price}")
        print(f"   Availability: {availability}")
        print(f"   Title: {title[:70]}{'...' if len(title) > 70 else ''}")
        print(f"   URL: {result.get('product_url', '#')}")
        print()

        if is_cheapest and not cheapest_found:
            cheapest_found = True

    # Summary message
    if amazon_is_cheapest:
        print("💡 Amazon has the best price for this product!")
    elif cheapest_found:
        print("💡 Found cheaper alternatives to Amazon!")
    else:
        print("💡 Prices need to be checked manually on the websites.")


def search_google(keyword, max_results=10, exclude_amazon=False):
    """Search Google for specific product pages on major retailer sites."""
    # Build the site search part
    if exclude_amazon:
        site_search = "(site:walmart.com/ip/ OR site:bestbuy.com/site/ OR site:target.com/p/ OR site:ebay.com/itm/ OR site:newegg.com/p/)"
    else:
        site_search = "(site:amazon.com/dp/ OR site:walmart.com/ip/ OR site:bestbuy.com/site/ OR site:target.com/p/ OR site:ebay.com/itm/ OR site:newegg.com/p/)"

    params = {
        "engine": "google",
        "q": f'"{keyword}" {site_search}',
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_API_KEY,
        "num": max_results * 2
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()

    organic_results = data.get("organic_results", [])
    products = []

    # Filter for actual product pages with specific URL patterns
    for item in organic_results:
        url = item.get("link", "")

        # Skip Amazon if exclude_amazon is True
        if exclude_amazon and "amazon.com" in url:
            continue

        # Check if it's actually a product page based on URL patterns
        is_product_page = any([
            "/dp/" in url and "amazon.com" in url,
            "/ip/" in url and "walmart.com" in url,
            "/site/" in url and "bestbuy.com" in url and ".p?" in url,
            "/p/" in url and "target.com" in url and "/A-" in url,
            "/itm/" in url and "ebay.com" in url,
            "/p/" in url and "newegg.com" in url,
        ])

        # Exclude category pages, search pages, and guides
        is_excluded = any([
            "/c/" in url, "/cp/" in url, "/buying-guides/" in url,
            "/abcat" in url, "/pcmcat" in url, "/s?" in url,
            "searchpage.jsp" in url, "/shop/" in url,
            "/brand/" in url, "/compare/" in url
        ])

        if is_product_page and not is_excluded and len(products) < max_results:
            store = urlparse(url).netloc.replace("www.", "") if url else "unknown"

            products.append({
                "title": item.get("title"),
                "product_url": url,
                "store": store,
                "price": "Check site"
            })

    return products

def extract_wholesaler_name(url):
    if isinstance(url, bytes):
        url = url.decode('utf-8')
    if not url:
        return "unknown"
    return urlparse(url).netloc.replace("www.", "")


def scrape_price_and_availability(url):
    """Scrape both price and availability from product page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        price = extract_price_from_page(soup, url)
        availability = extract_availability_from_page(soup)

        return price, availability

    except Exception as e:
        return "Check site", "Error"


def extract_price_from_page(soup, url):
    """Extract price from different retailer pages"""

    # Common price selectors for different sites
    price_selectors = {
        'amazon.com': [
            '.a-price-whole', '.a-price .a-offscreen', '.a-price-current',
            '[data-testid="price"] .a-price .a-offscreen', '.a-price-range'
        ],
        'walmart.com': [
            '[data-automation-id="product-price"]', '.price-current',
            '[data-testid="price-current"]', '.average-rating-stars + div'
        ],
        'bestbuy.com': [
            '.sr-only:contains("current price")', '.visually-hidden:contains("current price")',
            '.pricing-price__range', '.sr-only + .sr-only'
        ],
        'target.com': [
            '[data-test="product-price"]', '.h-display-xs',
            '[data-test="product-price-current"]'
        ],
        'ebay.com': [
            '.display-price', '.u-flL.condText', '.price .bold',
            '.it-price .bold', '.u-flL + .bold'
        ],
        'newegg.com': [
            '.product-buy-box .price-current', '.price-current-label + .price-current',
            '.product-price .price-current'
        ]
    }

    # Determine which site we're on
    site = None
    for domain in price_selectors.keys():
        if domain in url:
            site = domain
            break

    if not site:
        # Generic price extraction
        selectors = ['.price', '[class*="price"]', '[id*="price"]']
    else:
        selectors = price_selectors[site]

    # Try each selector
    for selector in selectors:
        try:
            if ':contains(' in selector:
                # Handle special selectors like :contains()
                if 'current price' in selector:
                    elements = soup.find_all(['span', 'div'], string=re.compile(r'current price', re.I))
                    for elem in elements:
                        parent = elem.parent
                        if parent:
                            price_text = parent.get_text(strip=True)
                            price = extract_numeric_price(price_text)
                            if price:
                                return f"${price}"
            else:
                elements = soup.select(selector)
                for elem in elements:
                    price_text = elem.get_text(strip=True)
                    price = extract_numeric_price(price_text)
                    if price and price > 0:  # Make sure it's a valid price
                        return f"${price}"
        except:
            continue

    # Fallback: look for any text that looks like a price
    price_pattern = r'\$[\d,]+\.?\d*'
    price_matches = re.findall(price_pattern, soup.get_text())
    if price_matches:
        # Get the most reasonable price (not too high, not too low)
        prices = []
        for match in price_matches:
            price = extract_numeric_price(match)
            if price and 1 <= price <= 10000:  # Reasonable price range
                prices.append(price)

        if prices:
            # Return the most common price or the first reasonable one
            return f"${min(prices)}"

    return "Check site"


def extract_availability_from_page(soup):
    """Extract availability from page"""
    text = soup.get_text().lower()

    if any(phrase in text for phrase in ['in stock', 'ships in', 'available', 'add to cart', 'buy now']):
        return "Yes"
    elif any(phrase in text for phrase in ['out of stock', 'unavailable', 'backorder', 'notify when available']):
        return "No"

    return "Not found"



def run_wholesaler_scraper(keyword):
    print(f"🔍 Searching Google for '{keyword}'...")
    products = search_google(keyword)
    results = []

    for product in products:
        url = product.get("product_url")
        store = product.get("store") or "unknown"
        print(f"🌐 Scraping price and availability for store: {store}")

        if url:
            price, availability = scrape_price_and_availability(url)
            wholesaler = extract_wholesaler_name(url)
        else:
            price = "No URL"
            availability = "No URL"
            wholesaler = "unknown"

        results.append({
            "wholesaler": wholesaler,
            "store": store,
            "title": product.get("title"),
            "price": price,  # This will now be actual scraped price
            "product_url": url,
            "availability": availability  # This will now be clean availability text
        })

        time.sleep(1)

    return results


# if __name__ == "__main__":
#     keyword = input("What would you like to search for? ")
#     results = run_wholesaler_scraper(keyword)
#
#     print("\n📦 Final Results:")
#     for i, result in enumerate(results, start=1):
#         print(f"{i}. {result}")


# quick test to see if that work
test_title = "Beats Solo 4 - Wireless Bluetooth On-Ear Headphones, Apple & Android Compatible, Up to 50 Hours of Battery Life - Matte Black (ASIN: B0CZPLV566)"
cleaned = clean_product_name_for_search(test_title)
print(f"Original: {test_title}")
print(f"Cleaned: {cleaned}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Search for any product")
    print("2. Find alternatives to Amazon product")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        keyword = input("What would you like to search for? ")
        results = run_wholesaler_scraper(keyword)

        print("\n📦 Final Results:")
        for i, result in enumerate(results, start=1):
            print(f"{i}. {result}")

    elif choice == "2":
        print("Paste the full Amazon product title (with ASIN):")
        amazon_title = input().strip()

        amazon_price = input("Enter Amazon price (optional, press Enter to skip): ").strip()
        amazon_price = amazon_price if amazon_price else None

        results = find_alternatives_to_amazon_product(amazon_title, amazon_price)
        display_price_comparison(results, amazon_title)

    else:
        print("Invalid choice")

