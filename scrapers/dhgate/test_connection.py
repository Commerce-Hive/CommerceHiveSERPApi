"""
Enhanced connection test for DHgate scraper with multiple strategies
"""

import sys
import os
import requests
import time

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from scrapers.dhgate.search import DHgateSearch


def test_basic_connectivity():
    """Test basic internet connectivity first"""
    print("🌐 Testing basic internet connectivity...")

    test_sites = [
        "https://httpbin.org/get",
        "https://google.com",
        "https://amazon.com"
    ]

    for site in test_sites:
        try:
            response = requests.get(site, timeout=10)
            if response.status_code == 200:
                print(f"✅ Internet connectivity OK - {site}")
                return True
        except Exception as e:
            print(f"❌ Failed to connect to {site}: {e}")
            continue

    print("❌ No internet connectivity detected")
    return False


def test_dhgate_alternatives():
    """Test alternative wholesale sites"""
    print("\n🔍 Testing alternative wholesale sites...")

    alternative_sites = [
        ("AliExpress", "https://www.aliexpress.com"),
        ("Alibaba", "https://www.alibaba.com"),
        ("Global Sources", "https://www.globalsources.com")
    ]

    working_sites = []

    for name, url in alternative_sites:
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                print(f"✅ {name} accessible - {url}")
                working_sites.append(name)
            else:
                print(f"⚠️ {name} returned status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} failed: {type(e).__name__}")

    return working_sites


def test_dhgate_with_different_methods():
    """Test DHgate with various connection methods"""
    print("\n🧪 Testing DHgate with different methods...")

    # Method 1: Simple requests
    print("\n1. Testing simple HTTP request...")
    try:
        response = requests.get("https://www.dhgate.com", timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        print(f"✅ Simple request worked - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Simple request failed: {type(e).__name__}")

    # Method 2: Mobile site
    print("\n2. Testing mobile site...")
    try:
        response = requests.get("https://m.dhgate.com", timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15'
        })
        print(f"✅ Mobile site worked - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Mobile site failed: {type(e).__name__}")

    # Method 3: Without HTTPS
    print("\n3. Testing HTTP (non-secure)...")
    try:
        response = requests.get("http://dhgate.com", timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        print(f"✅ HTTP worked - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ HTTP failed: {type(e).__name__}")

    # Method 4: With session and delays
    print("\n4. Testing with session and delays...")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })

        # First, try to visit a simple page
        time.sleep(2)
        response = session.get("https://www.dhgate.com/robots.txt", timeout=20)
        print(f"✅ Session + robots.txt worked - Status: {response.status_code}")

        time.sleep(3)
        response = session.get("https://www.dhgate.com", timeout=20)
        print(f"✅ Session + homepage worked - Status: {response.status_code}")
        return True

    except Exception as e:
        print(f"❌ Session method failed: {type(e).__name__}")

    return False


def test_dhgate_search_fallback():
    """Test if we can use our DHgate search with fallbacks"""
    print("\n🔍 Testing DHgate search with all bypass strategies...")

    try:
        search = DHgateSearch()
        connection_ok = search.test_connection()

        if connection_ok:
            print("✅ DHgate search bypass strategies worked!")
            return True
        else:
            print("❌ All DHgate bypass strategies failed")
            return False

    except Exception as e:
        print(f"❌ DHgate search test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Enhanced DHgate Connection Test")
    print("=" * 60)

    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("\n❌ Basic internet connectivity failed. Check your connection.")
        return

    # Test 2: Alternative sites
    working_alternatives = test_dhgate_alternatives()

    # Test 3: DHgate with different methods
    dhgate_works = test_dhgate_with_different_methods()

    # Test 4: Our enhanced search
    search_works = test_dhgate_search_fallback()

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if dhgate_works:
        print("✅ DHgate is accessible with basic methods")
    else:
        print("❌ DHgate is blocking basic connection attempts")

    if search_works:
        print("✅ Enhanced DHgate search strategies work")
    else:
        print("❌ All DHgate strategies failed")

    if working_alternatives:
        print(f"✅ Alternative sites available: {', '.join(working_alternatives)}")
    else:
        print("❌ No alternative wholesale sites accessible")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if dhgate_works or search_works:
        print("• DHgate scraping should work with the enhanced strategies")
        print("• Use longer delays between requests (3-5 seconds)")
        print("• Consider using the mobile site as fallback")
    elif working_alternatives:
        print("• DHgate appears to be blocking requests from your location/IP")
        print(f"• Consider using alternative sites: {', '.join(working_alternatives)}")
        print("• Try using a VPN or different network")
    else:
        print("• Network connectivity issues detected")
        print("• Check firewall/proxy settings")
        print("• Try from a different network")


if __name__ == "__main__":
    main()