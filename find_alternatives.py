from scraper import find_alternatives_to_amazon_product, display_price_comparison


def main():
    print("🔍 Amazon Price Comparison Tool")
    print("=" * 40)
    print("This tool will find the best prices across all retailers")
    print("(including Amazon if it's the cheapest option)")
    print()

    # Get Amazon product info
    print("Paste the full Amazon product title (including ASIN):")
    amazon_title = input().strip()

    if not amazon_title:
        print("❌ No title provided")
        return

    # Get Amazon price for comparison
    print("\nEnter the Amazon price (e.g., 199.99 or $199.99):")
    print("(Press Enter to skip if you don't know the price)")
    amazon_price_input = input().strip()

    # Clean the price input
    amazon_price = None
    if amazon_price_input:
        import re
        price_match = re.search(r'[\d,]+\.?\d*', amazon_price_input.replace(',', ''))
        if price_match:
            amazon_price = price_match.group()

    print(f"\n🔍 Searching for best prices...")

    # Find all alternatives including Amazon
    results = find_alternatives_to_amazon_product(amazon_title, amazon_price)

    if not results:
        print("❌ No results found")
        return

    # Use the enhanced display function
    display_price_comparison(results, amazon_title)

    # Additional summary
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION:")

    # Find if Amazon is cheapest
    amazon_results = [r for r in results if 'amazon.com' in r.get('store', '').lower()]
    amazon_is_cheapest = any(r.get('is_cheapest', False) for r in amazon_results)

    if amazon_is_cheapest:
        print("   🛒 Stick with Amazon - it has the best price!")
    else:
        cheapest = next((r for r in results if r.get('is_cheapest', False)), None)
        if cheapest:
            print(f"   💰 Save money! Buy from {cheapest['store'].upper()} instead of Amazon")
        else:
            print("   🔍 Check the prices manually on each website to compare")

    print("=" * 50)


if __name__ == "__main__":
    main()