from serpapi import GoogleSearch


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
        "offers" : True,
        "location": "Boston,Massachusetts,United States of America",
        "gl": "us", "hl": "en",
        "api_key": api_key,
    }
    search = GoogleSearch(params)
    data = search.get_dict()
    return data.get("product", {}).get("sellers_results", []).get("online_sellers", [])

def find_wholesalers(identifier, api_key):
    """
    Find wholesalers for a given product identifier (ASIN, UPC, etc.)
    :param identifier: ASIN, UPC, or product title/description
    :param api_key: Your SerpAPI key
    :return: List of wholesalers
    """

    results = shopping_search(identifier, api_key)
    if results is None: # change
        return []

    best = results[0]
    pid = best.get("product_id")
    # 2. Detailed seller fetch
    sellers = get_product_sellers(pid, api_key)
    return sellers

