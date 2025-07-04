"""
Amazon to DHgate Wholesale Finder
Find wholesale sources for Amazon retail products
"""

from product_lookup import get_top_products, show_products
from scrapers.dhgate.intelligent_search import find_wholesale_equivalent


def display_wholesale_comparison(amazon_product, dhgate_wholesale):
    """Display Amazon retail vs DHgate wholesale comparison"""

    print("\n" + "=" * 80)
    print("🏭 RETAIL TO WHOLESALE COMPARISON")
    print("=" * 80)

    print(f"\n📱 AMAZON RETAIL PRODUCT:")
    print(f"Title: {amazon_product['title']}")
    print(f"Retail Price: {amazon_product['price']}")
    print(f"ASIN: {amazon_product['asin']}")

    print(f"\n🏭 DHGATE WHOLESALE EQUIVALENTS:")
    print("-" * 60)

    if not dhgate_wholesale:
        print("❌ No wholesale equivalents found")
        return

    total_amazon_price = extract_price_number(amazon_product['price'])

    for i, product in enumerate(dhgate_wholesale, 1):
        similarity = product.get('similarity_score', 0)
        wholesale_price = product.get('price')

        print(f"\n{i}. {product['title'][:70]}{'...' if len(product['title']) > 70 else ''}")
        print(f"   🎯 Match Score: {similarity:.1f}% similarity")
        print(f"   💰 Wholesale Price: ${wholesale_price}")

        # Calculate potential savings
        if total_amazon_price and wholesale_price:
            savings = total_amazon_price - wholesale_price
            savings_percent = (savings / total_amazon_price) * 100
            print(f"   💵 Potential Savings: ${savings:.2f} ({savings_percent:.1f}% off retail)")

        print(f"   🏪 Seller: {product.get('seller', 'Unknown')}")
        print(f"   📦 Available: {'✅ Yes' if product.get('available') else '❌ No'}")

        # Bulk pricing info
        bulk_pricing = product.get('bulk_pricing')
        if bulk_pricing:
            print(f"   📊 Bulk Pricing Available: {len(bulk_pricing)} price tiers")

        # Shipping info
        shipping = product.get('shipping', {})
        if shipping.get('free_shipping'):
            print(f"   🚚 Shipping: Free")
        elif shipping.get('shipping_cost'):
            print(f"   🚚 Shipping: ${shipping['shipping_cost']}")

        if shipping.get('delivery_time'):
            print(f"   ⏰ Delivery: {shipping['delivery_time']}")

        print(f"   🔗 DHgate URL: {product['url']}")


def extract_price_number(price_str):
    """Extract numeric price from price string"""
    if not price_str:
        return None

    import re
    numbers = re.findall(r'[\d,]+\.?\d*', str(price_str).replace(',', ''))
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return None
    return None


def main():
    print("🏭 AMAZON TO DHGATE WHOLESALE FINDER")
    print("Find wholesale sources for Amazon retail products")
    print("=" * 60)

    # Step 1: Search Amazon
    search_term = input("\n🔍 Enter a product to find wholesale sources for: ").strip()

    print(f"\n📋 Searching Amazon for '{search_term}'...")
    amazon_products = get_top_products(search_term, max_results=10)

    if not amazon_products:
        print("❌ No Amazon products found.")
        return

    # Step 2: Select Amazon product
    show_products(amazon_products)

    try:
        choice = int(input("📝 Select product number to find wholesale equivalent: "))
        selected_amazon = amazon_products[choice - 1]

        print(f"\n✅ Selected: {selected_amazon['title']}")

        # Step 3: Find wholesale equivalents
        print(f"\n🔍 Searching DHgate for wholesale equivalents...")
        wholesale_products = find_wholesale_equivalent(selected_amazon['title'], max_results=5)

        # Step 4: Display comparison
        display_wholesale_comparison(selected_amazon, wholesale_products)

        # Step 5: Business insights
        if wholesale_products:
            show_business_insights(selected_amazon, wholesale_products)

    except (ValueError, IndexError):
        print("❌ Invalid selection.")


def show_business_insights(amazon_product, wholesale_products):
    """Show potential business/reselling insights"""

    print(f"\n💡 BUSINESS INSIGHTS")
    print("-" * 40)

    amazon_price = extract_price_number(amazon_product['price'])

    if not amazon_price or not wholesale_products:
        print("❌ Cannot calculate insights without price data")
        return

    best_wholesale = wholesale_products[0]  # Highest scored match
    wholesale_price = best_wholesale.get('price')

    if wholesale_price:
        margin = amazon_price - wholesale_price
        margin_percent = (margin / amazon_price) * 100

        print(f"📊 Best Wholesale Option:")
        print(f"   Amazon Retail: ${amazon_price}")
        print(f"   DHgate Wholesale: ${wholesale_price}")
        print(f"   Gross Margin: ${margin:.2f} ({margin_percent:.1f}%)")

        if margin_percent > 50:
            print(f"   🚀 HIGH MARGIN - Great for reselling!")
        elif margin_percent > 30:
            print(f"   ✅ GOOD MARGIN - Decent profit potential")
        elif margin_percent > 15:
            print(f"   ⚠️  LOW MARGIN - Consider fees and shipping")
        else:
            print(f"   ❌ VERY LOW MARGIN - May not be profitable")

        # Bulk pricing insights
        bulk_pricing = best_wholesale.get('bulk_pricing')
        if bulk_pricing:
            print(f"\n📦 Bulk Pricing Available:")
            for tier in bulk_pricing[:3]:  # Show top 3 tiers
                qty = tier.get('quantity')
                price = tier.get('price')
                if qty and price:
                    bulk_margin = amazon_price - price
                    bulk_margin_percent = (bulk_margin / amazon_price) * 100
                    print(f"   {qty}+ units: ${price} each ({bulk_margin_percent:.1f}% margin)")


if __name__ == "__main__":
    main()