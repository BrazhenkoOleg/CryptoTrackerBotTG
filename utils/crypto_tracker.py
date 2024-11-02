import requests
from config import API_KEY, SUPPORTED_CURRENCIES, SUPPORTED_CRYPTOCURRENCIES

BASE_URL = "https://min-api.cryptocompare.com/data/price"

def get_crypto_price(crypto='BTC', currency='USD'):
    params = {
        'fsym': crypto,
        'tsyms': currency,
        'api_key': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        return data.get(currency)
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def get_supported_currencies():
    return SUPPORTED_CURRENCIES
