import requests
from rapidfuzz import fuzz, process

SERP_API_KEY = "93f92def6771bede4c8f3b29b7a898e21bf2289ec589dc8ba905f760230a4c62"

def search_wholesalers(product_title, max_results=10):
    query = (
        f"{product_title} site:alibaba.com OR site:dhgate.com OR site:globalsources.com "
        f"OR site:walmart.com OR site:target.com OR site:ebay.com"
    )

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": max_results
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching SERP API results: {e}")
        return []

    results = []
    for result in data.get("organic_results", []):
        title = result.get("title", "No title")
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        results.append({
            "title": title,
            "snippet": snippet,
            "url": link
        })

    return results

def show_wholesaler_results(results, exact_title):
    if not results:
        print("No wholesaler listings found.")
        return

    # Compute similarity scores for each result title
    scored_results = []
    for product in results:
        similarity = fuzz.token_set_ratio(exact_title, product['title'])
        scored_results.append((similarity, product))

    # Sort descending by similarity
    scored_results.sort(key=lambda x: x[0], reverse=True)

    print(f"Top wholesaler matches for '{exact_title}':\n")
    for similarity, product in scored_results:
        print(f"Similarity: {similarity}%")
        print(f"Title: {product['title']}")
        print(f"URL: {product['url']}")
        print(f"Snippet: {product['snippet']}\n")
        if similarity < 60:
            print("Warning: This item may not be relevant as similarity score is below 60%.")
        print()  # Blank line for readability

def main():
    product_title = input("Enter exact product name: ").strip()
    results = search_wholesalers(product_title, max_results=10)
    show_wholesaler_results(results, product_title)

if __name__ == "__main__":
    main()
