import requests
from .config import settings

class AlphaVantageError(Exception):
    pass

BASE_URL = "https://www.alphavantage.co/query"

def fetch_daily(symbol: str) -> dict:
    params = {
        "function": "TIME_SERIES_DAILY",  
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": settings.alphavantage_api_key,
    }

    resp = requests.get(BASE_URL, params=params, timeout=30)
    data = resp.json()

    # --- Graceful error handling ---
    if "Error Message" in data:
        raise AlphaVantageError(data["Error Message"])

    if "Note" in data:
        raise AlphaVantageError(f"Rate limit hit: {data['Note']}")

    if "Information" in data:
        raise AlphaVantageError(f"Info: {data['Information']}")

    if "Time Series (Daily)" not in data:
        raise AlphaVantageError(f"Unexpected response keys: {list(data.keys())}")

    return data
