"""
Example usage of the DHgate scraper
"""

import json
import sys
import os

# Add the parent directory to the path so we can import the scrapers module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.dhgate.scraper import DHgateScraper


def main():
    """Example usage of the DHgate scraper"""

    # Initialize scraper
    scraper = DHgateScraper()

    # Example DHgate URLs for testing
    test_urls = [
        "https://www.dhgate.com/product/wireless-bluetooth-earphones-tws-earbuds/123456789.html",
        "https://www.dhgate.com/product/smart-watch-fitness-tracker/987654321.html",
        "https://www.dhgate.com/product/phone-case-protective-cover/555666777.html"
    ]

    print("=== DHgate Scraper Example ===\n")

    # Example 1: Scrape single product
    print("1. Scraping single product:")
    print("-" * 40)

    if test_urls:
        result = scraper.scrape_product(test_urls[0])
        print(f"URL: {result.get('url', 'N/A')}")

        if result.get('success'):
            print(f"✓ Success!")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Price: ${result.get('price', 'N/A')} {result.get('currency', '')}")
            print(f"  Available: {result.get('available', 'N/A')}")
            print(f"  Stock Status: {result.get('stock_status', 'N/A')}")

            if 'shipping' in result:
                shipping = result['shipping']
                print(f"  Shipping Cost: ${shipping.get('shipping_cost', 'N/A')}")
                print(f"  Delivery Time: {shipping.get('delivery_time', 'N/A')}")

            if result.get('seller'):
                print(f"  Seller: {result.get('seller')}")

            if result.get('rating'):
                print(f"  Rating: {result.get('rating')}/5")

            if result.get('review_count'):
                print(f"  Reviews: {result.get('review_count')}")

        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            if result.get('message'):
                print(f"  Message: {result.get('message')}")

    print("\n" + "=" * 50 + "\n")

    # Example 2: Scrape multiple products
    print("2. Scraping multiple products:")
    print("-" * 40)

    results = scraper.scrape_multiple_products(test_urls[:2])  # Limit to 2 for example

    for i, result in enumerate(results, 1):
        print(f"\nProduct {i}:")
        print(f"  URL: {result.get('url', 'N/A')}")

        if result.get('success'):
            print(f"  ✓ Title: {result.get('title', 'N/A')}")
            print(f"  ✓ Price: ${result.get('price', 'N/A')} {result.get('currency', '')}")
            print(f"  ✓ Available: {result.get('available', 'N/A')}")

            if 'shipping' in result:
                shipping_cost = result['shipping'].get('shipping_cost', 'N/A')
                print(f"  ✓ Shipping: ${shipping_cost}")
        else:
            print(f"  ✗ Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 50 + "\n")

    # Example 3: Full JSON output
    print("3. Full JSON output (first product):")
    print("-" * 40)

    if results:
        print(json.dumps(results[0], indent=2, default=str))


def test_with_real_urls():
    """Test with real DHgate URLs (if available)"""

    # Replace these with actual DHgate product URLs for testing
    real_urls = [
        # Add real DHgate URLs here for testing
        # "https://www.dhgate.com/product/actual-product-url/123456789.html"
    ]

    if not real_urls:
        print("No real URLs provided for testing.")
        return

    scraper = DHgateScraper()

    print("=== Testing with Real URLs ===\n")

    for i, url in enumerate(real_urls, 1):
        print(f"Testing URL {i}: {url}")
        result = scraper.scrape_product(url)

        if result.get('success'):
            print(f"✓ Success: {result.get('title', 'N/A')}")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown')}")

        print("-" * 40)


if __name__ == "__main__":
    main()

    # Uncomment to test with real URLs
    # test_with_real_urls()