import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

SERPAPI_API_KEY = "93f92def6771bede4c8f3b29b7a898e21bf2289ec589dc8ba905f760230a4c62"
print("API Key:", SERPAPI_API_KEY)


def search_google(keyword, max_results=10):
    """Search Google for specific product pages on major retailer sites."""
    # Search for actual product pages with correct URL patterns for any product
    params = {
        "engine": "google",
        "q": f'"{keyword}" (site:amazon.com/dp/ OR site:walmart.com/ip/ OR site:bestbuy.com/site/ OR site:target.com/p/ OR site:ebay.com/itm/ OR site:newegg.com/p/)',
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_API_KEY,
        "num": max_results * 2  # Get more results to filter
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()

    organic_results = data.get("organic_results", [])
    products = []

    # Filter for actual product pages with specific URL patterns
    for item in organic_results:
        url = item.get("link", "")

        # Check if it's actually a product page based on URL patterns
        is_product_page = any([
            "/dp/" in url and "amazon.com" in url,
            "/ip/" in url and "walmart.com" in url,
            "/site/" in url and "bestbuy.com" in url and ".p?" in url,  # Best Buy product pages end with .p?
            "/p/" in url and "target.com" in url and "/A-" in url,  # Target format: /p/product-name/-/A-12345
            "/itm/" in url and "ebay.com" in url,
            "/p/" in url and "newegg.com" in url,
        ])

        # Exclude category pages, search pages, and guides
        is_excluded = any([
            "/c/" in url,  # category pages
            "/cp/" in url,  # category pages
            "/buying-guides/" in url,
            "/abcat" in url,  # Best Buy category pages
            "/pcmcat" in url,  # Best Buy category pages
            "/s?" in url,  # Amazon search results pages
            "searchpage.jsp" in url,  # Best Buy search pages
            "/shop/" in url,  # generic shop pages
            "/brand/" in url,  # brand pages
            "/compare/" in url,  # comparison pages
        ])

        if is_product_page and not is_excluded and len(products) < max_results:
            store = urlparse(url).netloc.replace("www.", "") if url else "unknown"

            products.append({
                "title": item.get("title"),
                "product_url": url,
                "store": store,
                "price": "Check site"
            })

    # If we still don't have enough specific product results, do a more targeted search
    if len(products) < max_results // 2:
        # Try searching for products with purchase intent keywords
        broader_params = {
            "engine": "google",
            "q": f'{keyword} ("buy now" OR "price" OR "add to cart") (site:amazon.com OR site:walmart.com OR site:bestbuy.com OR site:target.com OR site:ebay.com OR site:newegg.com)',
            "hl": "en",
            "gl": "us",
            "api_key": SERPAPI_API_KEY,
            "num": max_results
        }

        broader_response = requests.get("https://serpapi.com/search", params=broader_params)
        broader_response.raise_for_status()
        broader_data = broader_response.json()

        for item in broader_data.get("organic_results", []):
            if len(products) >= max_results:
                break

            url = item.get("link", "")
            store = urlparse(url).netloc.replace("www.", "") if url else "unknown"

            # Skip excluded pages and duplicates
            is_excluded = any([
                "/c/" in url, "/cp/" in url, "/buying-guides/" in url, "/abcat" in url,
                "/pcmcat" in url, "/s?" in url, "searchpage.jsp" in url, "/shop/" in url,
                "/brand/" in url, "/compare/" in url
            ])

            if is_excluded:
                continue

            # Skip if we already have this exact URL
            if any(p['product_url'] == url for p in products):
                continue

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

def scrape_availability(url):
    """Attempt to scrape availability info from product page and classify it."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        for tag in soup.find_all(['span', 'div', 'p']):
            text = tag.get_text(strip=True).lower()

            if 'in stock' in text or 'ships in' in text or 'available' in text:
                return "Yes"
            elif 'out of stock' in text or 'unavailable' in text or 'backorder' in text:
                return "No"

        return "Not found"
    except Exception:
        return "Error"

def run_wholesaler_scraper(keyword):
    print(f"🔍 Searching Google for '{keyword}'...")
    products = search_google(keyword)
    results = []

    for product in products:
        url = product.get("product_url")
        store = product.get("store") or "unknown"
        print(f"🌐 Scraping availability for store: {store}")

        if url:
            availability = scrape_availability(url)
            wholesaler = extract_wholesaler_name(url)
        else:
            availability = "No URL"
            wholesaler = "unknown"

        results.append({
            "wholesaler": wholesaler,
            "store": store,
            "title": product.get("title"),
            "price": "Check site",
            "product_url": url,
            "availability": availability
        })

        time.sleep(1)

    return results

if __name__ == "__main__":
    keyword = input("What would you like to search for? ")
    results = run_wholesaler_scraper(keyword)

    print("\n📦 Final Results:")
    for i, result in enumerate(results, start=1):
        print(f"{i}. {result}")
