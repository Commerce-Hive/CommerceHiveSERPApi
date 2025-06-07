import pytest
from unittest.mock import patch
from main import shopping_search, get_product_sellers, find_wholesalers


@pytest.fixture
def mock_api_key():
    return "mock_api_key"


@pytest.fixture
def mock_shopping_response():
    return {
        "shopping_results": [
            {"product_id": "12345", "title": "USB C fast charger 65W", "price": "$19.99"},
            {"product_id": "67890", "title": "Wireless Mouse", "price": "$25.99"}
        ]
    }


@pytest.fixture
def mock_sellers_response():
    return {
        "product": {
            "sellers_results": {
                "online_sellers": [
                    {"name": "Wholesaler A", "price": "$18.99"},
                    {"name": "Wholesaler B", "price": "$17.99"}
                ]
            }
        }
    }


@patch("main.GoogleSearch")
def test_shopping_search(mock_google_search, mock_api_key, mock_shopping_response):
    mock_google_search.return_value.get_dict.return_value = mock_shopping_response
    results = shopping_search("USB C fast charger 65W", mock_api_key)
    assert len(results) == 2
    assert results[0]["product_id"] == "12345"
    assert results[0]["title"] == "USB C fast charger 65W"


@patch("main.GoogleSearch")
def test_get_product_sellers(mock_google_search, mock_api_key, mock_sellers_response):
    mock_google_search.return_value.get_dict.return_value = mock_sellers_response
    sellers = get_product_sellers("12345", mock_api_key)
    assert len(sellers) == 2
    assert sellers[0]["name"] == "Wholesaler A"
    assert sellers[1]["price"] == "$17.99"


@patch("main.shopping_search")
@patch("main.get_product_sellers")
def test_find_wholesalers(mock_get_product_sellers, mock_shopping_search, mock_api_key, mock_shopping_response,
                          mock_sellers_response):
    mock_shopping_search.return_value = mock_shopping_response["shopping_results"]
    mock_get_product_sellers.return_value = mock_sellers_response["product"]["sellers_results"]["online_sellers"]
    wholesalers = find_wholesalers("USB C fast charger 65W", mock_api_key)
    assert len(wholesalers) == 2
    assert wholesalers[0]["name"] == "Wholesaler A"
    assert wholesalers[1]["price"] == "$17.99"
