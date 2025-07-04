"""
Intelligent search for finding DHgate wholesale equivalents of Amazon retail products
"""

import re
from .search import DHgateSearch
from .utils import DHgateUtils


class IntelligentDHgateSearch(DHgateSearch):
    """Enhanced search that finds wholesale equivalents of retail products"""

    def __init__(self):
        super().__init__()
        self.utils = DHgateUtils()

    def find_wholesale_equivalent(self, amazon_title, max_results=10):
        """
        Find DHgate wholesale products that match an Amazon retail product
        Uses multiple search strategies to find the best matches
        """
        print(f"🎯 Finding wholesale equivalent for: {amazon_title}")

        # Generate multiple search variations
        search_terms = self._generate_search_variations(amazon_title)

        all_results = []

        # Try each search term
        for i, term in enumerate(search_terms[:3]):  # Limit to top 3 variations
            print(f"🔍 Search variation {i + 1}: '{term}'")

            results = self.search_products(term, max_results=5)

            # Score and rank results based on similarity to original
            scored_results = self._score_similarity(amazon_title, results)
            all_results.extend(scored_results)

        # Remove duplicates and sort by score
        unique_results = self._deduplicate_results(all_results)
        sorted_results = sorted(unique_results, key=lambda x: x.get('similarity_score', 0), reverse=True)

        return sorted_results[:max_results]

    def _generate_search_variations(self, amazon_title):
        """Generate multiple search term variations to find wholesale equivalents"""

        # 1. Extract core product keywords
        core_keywords = self._extract_core_keywords(amazon_title)

        # 2. Remove brand names (wholesale might not have same brand)
        generic_title = self._remove_brand_names(amazon_title)

        # 3. Focus on product type and key features
        feature_focused = self._extract_key_features(amazon_title)

        # 4. Add wholesale-specific terms
        wholesale_variations = self._add_wholesale_terms(core_keywords)

        variations = [
            core_keywords,
            generic_title,
            feature_focused,
            wholesale_variations,
            # Combinations
            f"{core_keywords} wholesale",
            f"{feature_focused} bulk",
        ]

        # Clean and filter variations
        clean_variations = []
        for var in variations:
            if var and len(var.strip()) > 3:
                clean_variations.append(var.strip())

        return clean_variations

    def _extract_core_keywords(self, title):
        """Extract the most important product keywords"""

        # Remove common Amazon-specific terms
        amazon_terms = [
            'amazon', 'prime', 'eligible', 'brand:', 'asin:',
            '- amazon', 'amazon.com', 'fulfillment by amazon'
        ]

        clean_title = title.lower()
        for term in amazon_terms:
            clean_title = re.sub(term, '', clean_title, flags=re.IGNORECASE)

        # Extract main product type and key descriptors
        important_words = []

        # Product categories that are important
        product_types = [
            'headphones', 'earbuds', 'speaker', 'phone case', 'charger', 'cable',
            'watch', 'fitness tracker', 'mouse', 'keyboard', 'laptop stand',
            'bluetooth', 'wireless', 'usb', 'led', 'smart', 'portable'
        ]

        words = clean_title.split()
        for word in words:
            word = re.sub(r'[^\w]', '', word)  # Remove punctuation
            if len(word) > 2:
                # Keep product types, technical specs, and colors
                if (word in product_types or
                        any(spec in word for spec in ['wireless', 'bluetooth', 'usb', 'led']) or
                        any(color in word for color in ['black', 'white', 'blue', 'red', 'silver']) or
                        re.match(r'\d+', word)):  # Numbers (like 64gb, 15w, etc.)
                    important_words.append(word)

        return ' '.join(important_words[:6])  # Limit to 6 most important words

    def _remove_brand_names(self, title):
        """Remove brand names since wholesale might not have same brands"""

        common_brands = [
            'apple', 'samsung', 'sony', 'beats', 'bose', 'jbl', 'anker',
            'logitech', 'razer', 'corsair', 'hp', 'dell', 'lenovo',
            'nike', 'adidas', 'amazon', 'google', 'microsoft'
        ]

        clean_title = title
        for brand in common_brands:
            clean_title = re.sub(brand, '', clean_title, flags=re.IGNORECASE)

        # Clean up extra spaces
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        return clean_title

    def _extract_key_features(self, title):
        """Focus on key product features that matter for wholesale"""

        # Technical specifications that matter
        tech_patterns = [
            r'bluetooth\s*\d*\.?\d*',
            r'wireless',
            r'usb[-\s]?c?',
            r'\d+gb',
            r'\d+tb',
            r'\d+w\b',  # watts
            r'\d+v\b',  # volts
            r'\d+\s*inch',
            r'\d+\s*ft',
            r'waterproof',
            r'fast\s*charg\w*',
            r'quick\s*charg\w*'
        ]

        features = []
        title_lower = title.lower()

        for pattern in tech_patterns:
            matches = re.findall(pattern, title_lower)
            features.extend(matches)

        # Product type (usually the first few words)
        words = title.split()
        product_type = ' '.join(words[:3])  # First 3 words usually describe the product

        if features:
            return f"{product_type} {' '.join(features)}"
        else:
            return product_type

    def _add_wholesale_terms(self, core_keywords):
        """Add terms that might help find wholesale versions"""

        wholesale_terms = ['wholesale', 'bulk', 'factory', 'oem', 'generic']

        # Try adding one wholesale term
        return f"{core_keywords} {wholesale_terms[0]}"

    def _score_similarity(self, original_title, dhgate_results):
        """Score DHgate results based on similarity to original Amazon product"""

        scored_results = []
        original_words = set(original_title.lower().split())

        for result in dhgate_results:
            dhgate_title = result.get('title', '')
            dhgate_words = set(dhgate_title.lower().split())

            # Calculate similarity score
            score = self._calculate_similarity_score(original_words, dhgate_words, result)

            result['similarity_score'] = score
            result['original_amazon_title'] = original_title

            scored_results.append(result)

        return scored_results

    def _calculate_similarity_score(self, original_words, dhgate_words, result):
        """Calculate a similarity score between Amazon and DHgate products"""

        score = 0

        # 1. Word overlap (30% of score)
        common_words = original_words.intersection(dhgate_words)
        word_score = len(common_words) / len(original_words) * 30
        score += word_score

        # 2. Key feature matching (40% of score)
        key_features = ['bluetooth', 'wireless', 'usb', 'led', 'smart', 'portable']
        feature_matches = 0

        for feature in key_features:
            if (any(feature in word for word in original_words) and
                    any(feature in word for word in dhgate_words)):
                feature_matches += 1

        if key_features:
            feature_score = (feature_matches / len(key_features)) * 40
            score += feature_score

        # 3. Price reasonableness (20% of score)
        # Wholesale should be significantly cheaper
        price = result.get('price')
        if isinstance(price, (int, float)) and price > 0:
            if price < 50:  # Very reasonable wholesale price
                score += 20
            elif price < 100:
                score += 10

        # 4. Availability bonus (10% of score)
        if result.get('available'):
            score += 10

        return min(score, 100)  # Cap at 100

    def _deduplicate_results(self, results):
        """Remove duplicate results based on URL or very similar titles"""

        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get('url', '')
            title = result.get('title', '').lower()

            # Skip if we've seen this URL
            if url in seen_urls:
                continue

            # Skip if we have a very similar title
            is_duplicate = False
            for existing in unique_results:
                existing_title = existing.get('title', '').lower()
                if self._titles_very_similar(title, existing_title):
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _titles_very_similar(self, title1, title2, threshold=0.8):
        """Check if two titles are very similar (likely duplicates)"""

        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        similarity = intersection / union if union > 0 else 0

        return similarity >= threshold


def find_wholesale_equivalent(amazon_title, max_results=5):
    """
    Main function to find DHgate wholesale equivalents of Amazon retail products
    """
    searcher = IntelligentDHgateSearch()
    return searcher.find_wholesale_equivalent(amazon_title, max_results)