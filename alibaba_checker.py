import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def is_alibaba_url(url):
    """Check if the URL is from Alibaba domain."""
    parsed = urlparse(url)
    return "alibaba.com" in parsed.netloc

def fetch_page(url):
    """Request the page and return soup object, or None if error like 404."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            print("Page returned 404 Not Found.")
            return None
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def detect_and_follow_category_page(soup, base_url):
    """Detect if it's a category/search page and try to follow the first item."""
    product_links = soup.select('a[href*="/product-detail/"]')
    for link in product_links:
        href = link.get('href')
        if href and "/product-detail/" in href:
            full_url = urljoin(base_url, href)
            print(f"➡️ Detected category page. Redirecting to first product: {full_url}")
            return fetch_page(full_url), full_url
    print("No product link found on category page.")
    return None, None

def check_availability(soup):
    """More precise check for Alibaba product availability."""
    # Look for Min Order Quantity
    moq_section = soup.find(string=lambda s: s and "Min. order" in s)
    if moq_section:
        return True

    # Look for 'Add to Cart' or 'Contact Supplier' buttons
    buttons = soup.find_all('button')
    for btn in buttons:
        if btn.get_text(strip=True).lower() in ['contact supplier', 'add to cart']:
            return True

    # Fallback for known stock-related classes
    for tag in soup.select('.quantity, .availability, .sku-text'):
        text = tag.get_text(strip=True).lower()
        if "out of stock" in text or "unavailable" in text:
            return False
        if "in stock" in text or "available" in text:
            return True

    return False  # Default to unavailable if no clear signs

def extract_price(soup):
    """Try to extract price range or price from the page."""
    price_tags = soup.find_all(['span', 'div'], string=lambda s: s and '$' in s)
    for tag in price_tags:
        price = tag.get_text(strip=True)
        if "$" in price:
            return price
    return "Price not found"

def main():
    url = input("--> Enter Alibaba product URL: ").strip()

    if not is_alibaba_url(url):
        print(" Not a valid Alibaba URL.")
        return

    soup = fetch_page(url)
    if not soup:
        return

    # Failsafe: detect category/search/listing page
    if "/category/" in url or "/products/" in url or "SearchText=" in url:
        soup, url = detect_and_follow_category_page(soup, url)
        if not soup:
            print("Could not retrieve product from category/listing page.")
            return

    is_available = check_availability(soup)
    if not is_available:
        print("Product is unavailable or out of stock.")
        return

    price = extract_price(soup)
    print("\nProduct is available!")
    print(f"Price Info: {price}")
    print(f"Product URL: {url}")

if __name__ == "__main__":
    main()