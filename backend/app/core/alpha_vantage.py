import requests
from typing import Any, Dict
from .config import settings

BASE_URL = "https://www.alphavantage.co/query"

class AlphaVantageError(RuntimeError):
    pass

def fetch_daily_adjusted(ticker: str) -> Dict[str, Any]:
    if not settings.alphavantage_api_key:
        raise AlphaVantageError("ALPHAVANTAGE_API_KEY is not set.")
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": "compact",
        "apikey": settings.alphavantage_api_key,
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "Error Message" in data:
        raise AlphaVantageError(data["Error Message"])
    if "Note" in data:
        # rate limit
        raise AlphaVantageError(data["Note"])
    if "Time Series (Daily)" not in data:
        raise AlphaVantageError(f"Unexpected Alpha Vantage response keys: {list(data.keys())}")
    return data
