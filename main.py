from serpapi import GoogleSearch
from scrapers.dhgate.search import DHgateSearch


def shopping_search(query, api_key, location="Boston,Massachusetts,United States of America"):
    """
    Perform a Google Shopping search.
    :param query:
    :param api_key:
    :param location:
    :return: the search results as a list of dictionaries.
    """
    params = {
        "engine": "google_shopping",
        "q": query,  # ASIN, UPC, product title/description
        "api_key": api_key,
        "location": location
    }
    search = GoogleSearch(params)
    return search.get_dict().get("shopping_results", [])


def get_product_sellers(product_id, api_key):
    params = {
        "engine": "google_shopping_product",
        "product_id": product_id,
        "offers": True,
        "location": "Boston,Massachusetts,United States of America",
        "gl": "us", "hl": "en",
        "api_key": api_key,
    }
    search = GoogleSearch(params)
    data = search.get_dict()
    return data.get("product", {}).get("sellers_results", {}).get("online_sellers", [])


def find_dhgate_wholesalers(product_name, max_results=5):
    """
    Find DHgate wholesale options for a product
    :param product_name: Product name to search for
    :param max_results: Maximum number of results to return
    :return: List of DHgate wholesale products
    """
    print(f"\n🔍 Searching DHgate for wholesale options: '{product_name}'")

    try:
        dhgate_search = DHgateSearch()
        results = dhgate_search.search_products(product_name, max_results=max_results)

        if results:
            print(f"✅ Found {len(results)} DHgate wholesale options")
            return results
        else:
            print("⚠️ No DHgate results found")
            return []

    except Exception as e:
        print(f"❌ DHgate search failed: {e}")
        return []


def find_wholesalers(identifier, api_key, include_dhgate=True):
    """
    Find wholesalers for a given product identifier (ASIN, UPC, etc.)
    :param identifier: ASIN, UPC, or product title/description
    :param api_key: Your SerpAPI key
    :param include_dhgate: Whether to include DHgate wholesale search
    :return: Dictionary with Google sellers and DHgate results
    """

    # 1. Get Google Shopping results
    print(f"🔍 Searching Google Shopping for: '{identifier}'")
    results = shopping_search(identifier, api_key)

    if not results:
        print("⚠️ No Google Shopping results found")
        google_sellers = []
    else:
        best = results[0]
        pid = best.get("product_id")
        print(f"📦 Found product: {best.get('title', 'Unknown')}")

        # 2. Get detailed seller info
        google_sellers = get_product_sellers(pid, api_key)
        print(f"🏪 Found {len(google_sellers)} Google sellers")

    # 3. Get DHgate wholesale options
    dhgate_results = []
    if include_dhgate:
        # Use the product title from Google results if available
        search_term = identifier
        if results and results[0].get('title'):
            search_term = results[0]['title']

        dhgate_results = find_dhgate_wholesalers(search_term, max_results=5)

    return {
        'google_sellers': google_sellers,
        'dhgate_wholesale': dhgate_results,
        'total_options': len(google_sellers) + len(dhgate_results)
    }


def display_wholesale_results(results):
    """
    Display wholesale results in a nice format
    """
    print("\n" + "=" * 60)
    print("📊 WHOLESALE SEARCH RESULTS")
    print("=" * 60)

    # Display Google sellers
    google_sellers = results.get('google_sellers', [])
    if google_sellers:
        print(f"\n🛒 GOOGLE SHOPPING SELLERS ({len(google_sellers)} found):")
        print("-" * 40)
        for i, seller in enumerate(google_sellers[:5], 1):
            name = seller.get('name', 'Unknown Seller')
            price = seller.get('price', 'Price not listed')
            rating = seller.get('rating', 'No rating')
            print(f"{i}. {name}")
            print(f"   💰 Price: {price}")
            print(f"   ⭐ Rating: {rating}")
            print()
    else:
        print("\n🛒 No Google Shopping sellers found")

    # Display DHgate results
    dhgate_results = results.get('dhgate_wholesale', [])
    if dhgate_results:
        print(f"\n🏭 DHGATE WHOLESALE OPTIONS ({len(dhgate_results)} found):")
        print("-" * 40)
        for i, product in enumerate(dhgate_results, 1):
            title = product.get('title', 'No title')[:60]
            price = product.get('price', 'No price')
            seller = product.get('seller', 'Unknown seller')
            available = product.get('available', False)

            print(f"{i}. {title}...")
            print(f"   💰 Price: ${price}")
            print(f"   🏪 Seller: {seller}")
            print(f"   📦 Available: {'✅' if available else '❌'}")
            print(f"   🔗 URL: {product.get('url', 'N/A')[:50]}...")
            print()
    else:
        print("\n🏭 No DHgate wholesale options found")

    total = results.get('total_options', 0)
    print(f"\n📈 TOTAL WHOLESALE OPTIONS FOUND: {total}")
    print("=" * 60)


# Example usage function
def main_example():
    """Example of how to use the enhanced wholesale finder"""

    # You'll need to set your SerpAPI key
    api_key = "your_serpapi_key_here"  # Replace with your actual key

    # Example searches
    test_products = [
        "wireless earbuds",
        "phone case iPhone",
        "bluetooth speaker",
    ]

    for product in test_products:
        print(f"\n{'=' * 60}")
        print(f"🔍 SEARCHING FOR: {product.upper()}")
        print('=' * 60)

        # Find wholesale options
        results = find_wholesalers(product, api_key, include_dhgate=True)

        # Display results
        display_wholesale_results(results)

        # Wait between searches
        input("\nPress Enter to continue to next product...")


if __name__ == "__main__":
    # Uncomment to run the example
    # main_example()

    # For testing without SerpAPI key, test just DHgate
    print("🧪 Testing DHgate wholesale search only...")
    dhgate_results = find_dhgate_wholesalers("phone case", max_results=3)

    if dhgate_results:
        print(f"\n✅ Found {len(dhgate_results)} DHgate products:")
        for i, product in enumerate(dhgate_results, 1):
            title = product.get('title', 'No title')[:50]
            price = product.get('price', 'No price')
            print(f"{i}. {title}... - ${price}")
    else:
        print("❌ No DHgate results found")