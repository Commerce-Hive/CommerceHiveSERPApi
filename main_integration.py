"""
Integration example: Amazon product lookup + DHgate alternatives
"""

import sys
import os

# Add scrapers to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_lookup import get_top_products, show_products
from scrapers.dhgate.search import find_dhgate_alternatives


def clean_amazon_title(full_title):
    """Clean Amazon title for better search results"""
    import re

    # Remove ASIN
    title = re.sub(r'\(ASIN:.*?\)', '', full_title).strip()

    # Remove Amazon-specific terms
    title = re.sub(r'- (Amazon|Prime|Eligible)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'Amazon\.com', '', title, flags=re.IGNORECASE)

    # Keep only the core product name and key features
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


def display_comparison(amazon_product, dhgate_alternatives):
    """Display Amazon vs DHgate comparison"""
    print("\n" + "=" * 80)
    print("🛒 PRODUCT COMPARISON")
    print("=" * 80)

    print(f"\n📦 AMAZON PRODUCT:")
    print(f"Title: {amazon_product['title']}")
    print(f"Price: {amazon_product['price']}")
    print(f"ASIN: {amazon_product['asin']}")

    print(f"\n🏭 DHGATE ALTERNATIVES:")
    print("-" * 60)

    if not dhgate_alternatives:
        print("❌ No DHgate alternatives found")
        return

    for i, alt in enumerate(dhgate_alternatives, 1):
        print(f"\n{i}. {alt['title'][:70]}{'...' if len(alt['title']) > 70 else ''}")
        print(f"   💰 Price: {alt['price']} {alt['currency']}")
        print(f"   🏪 Seller: {alt['seller']}")
        print(f"   📦 Available: {'✅ Yes' if alt['available'] else '❌ No'}")

        if alt['rating']:
            print(f"   ⭐ Rating: {alt['rating']}/5")

        if alt['review_count']:
            print(f"   📝 Reviews: {alt['review_count']}")

        shipping = alt.get('shipping', {})
        if shipping.get('free_shipping'):
            print(f"   🚚 Shipping: Free")
        elif shipping.get('shipping_cost'):
            print(f"   🚚 Shipping: ${shipping['shipping_cost']}")

        if shipping.get('delivery_time'):
            print(f"   ⏰ Delivery: {shipping['delivery_time']}")

        print(f"   🔗 URL: {alt['url']}")


def main():
    print("🛍️  AMAZON TO DHGATE ALTERNATIVE FINDER")
    print("=" * 50)

    # Step 1: Search Amazon products
    search_term = input("\n🔍 Enter a product to search for: ").strip()

    print(f"\n📋 Searching Amazon for '{search_term}'...")
    amazon_products = get_top_products(search_term, max_results=10)

    if not amazon_products:
        print("❌ No Amazon products found. Try a different search term.")
        return

    # Step 2: Show Amazon products and let user select
    show_products(amazon_products)

    try:
        choice = int(input("📝 Select a product number to find DHgate alternatives: "))
        selected_product = amazon_products[choice - 1]

        print(f"\n✅ Selected: {selected_product['title']}")

        # Step 3: Clean the title and search DHgate
        clean_title = clean_amazon_title(selected_product['title'])
        print(f"🧹 Cleaned search term: {clean_title}")

        # Step 4: Find DHgate alternatives
        print(f"\n🔍 Searching DHgate for alternatives...")
        dhgate_alternatives = find_dhgate_alternatives(clean_title, max_results=5)

        # Step 5: Display comparison
        display_comparison(selected_product, dhgate_alternatives)

        # Step 6: Save results (optional)
        save_choice = input(f"\n💾 Save results to file? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_results(selected_product, dhgate_alternatives)

    except (ValueError, IndexError):
        print("❌ Invalid selection. Please try again.")


def save_results(amazon_product, dhgate_alternatives):
    """Save comparison results to a file"""
    import json
    from datetime import datetime

    results = {
        'search_date': datetime.now().isoformat(),
        'amazon_product': amazon_product,
        'dhgate_alternatives': dhgate_alternatives,
        'total_alternatives_found': len(dhgate_alternatives)
    }

    filename = f"amazon_dhgate_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"💾 Results saved to: {filename}")


if __name__ == "__main__":
    main()