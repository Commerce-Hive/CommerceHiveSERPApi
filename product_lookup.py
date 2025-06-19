import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("RAINFOREST_API_KEY")

RAINFOREST_ENDPOINT = "https://api.rainforestapi.com/request"


def get_top_products(search_term, max_results=20):
    params = {
        "api_key": API_KEY,
        "type": "search",
        "amazon_domain": "amazon.com",
        "search_term": search_term,
        "page": 1
    }

    response = requests.get(RAINFOREST_ENDPOINT, params=params)
    data = response.json()

    results = []
    for item in data.get("search_results", [])[:max_results]:
        title = item.get("title", "No title")
        asin = item.get("asin", "N/A")
        price = item.get("price", {}).get("raw", "Price not listed")
        results.append({
            "title": title,
            "asin": asin,
            "price": price
        })

    return results


def show_products(products):
    print("\nTop Products Found:\n")
    for idx, product in enumerate(products, start=1):
        print(f"{idx}. {product['title']} - {product['price']}")
    print()


def main():
    user_input = input("Enter a product category or keyword (e.g., shoes, headphones): ").strip()

    print("\nSearching Amazon...\n")
    products = get_top_products(user_input)

    if not products:
        print("No products found. Try a different keyword.")
        return

    show_products(products)

    # Next step hand-off: get user selection
    try:
        choice = int(input("Enter the number of the product to use for wholesale lookup: "))
        selected = products[choice - 1]
        print(f"\nYou selected: {selected['title']} (ASIN: {selected['asin']})")
        # Pass `selected['title']` to next step (SERP API team)
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")


if __name__ == "__main__":
    main()
