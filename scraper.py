import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

SERPAPI_API_KEY = "93f92def6771bede4c8f3b29b7a898e21bf2289ec589dc8ba905f760230a4c62"
print("API Key:", SERPAPI_API_KEY)

def search_google(keyword, max_results=10):
    """Search Google via SerpAPI and return organic result URLs."""
    params = {
        "engine": "google",
        "q": keyword,
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_API_KEY,
        "num": max_results
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()

    organic_results = data.get("organic_results", [])
    products = []

    for item in organic_results[:max_results]:
        products.append({
            "title": item.get("title"),
            "product_url": item.get("link"),
            "store": urlparse(item.get("link", "")).netloc.replace("www.", "")
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
