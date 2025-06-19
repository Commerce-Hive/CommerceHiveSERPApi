import unittest
from unittest.mock import patch, Mock
from product_lookup import get_top_products, show_products

class TestApiCalls(unittest.TestCase):
    def setUp(self):
        self.search_term = "shoes"

    @patch('product_lookup.requests.get')
    def test_get_top_products(self, mock_get):
        product_data = {
            "search_results": [
                {"title": "Product 1", "asin": "1234", "price": {"raw": "10.00"}},
                {"title": "Product 2", "asin": "5678", "price": {"raw": "20.00"}}
            ]
        }

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = product_data

        products = get_top_products(self.search_term)

        # Check the function behavior
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]['title'], 'Product 1')
        self.assertEqual(products[0]['asin'], '1234')
        self.assertEqual(products[0]['price'], '10.00')

    @patch('builtins.print')
    def test_show_products(self, mock_print):
        products = [
            {'title': 'Product 1', 'asin': '1234', 'price': '10.00'},
            {'title': 'Product 2', 'asin': '5678', 'price': '20.00'}
        ]

        show_products(products)

        # Checking the function behavior
        calls = [
            unittest.mock.call("\nTop Products Found:\n"),
            unittest.mock.call("1. Product 1 - 10.00"),
            unittest.mock.call("2. Product 2 - 20.00"),
            unittest.mock.call()
        ]
        mock_print.assert_has_calls(calls, any_order=False)


if __name__ == '__main__':
    unittest.main()