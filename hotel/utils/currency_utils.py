import requests
from decimal import Decimal
from django.conf import settings

def convert_currency(amount, from_currency="USD", to_currency="INR"):
    """
    Converts amount from one currency to another using ExchangeRate-API.
    """
    base_url = settings.EXCHANGE_RATE_BASE_URL
    url = f"{base_url}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and "conversion_rates" in data:
            rates = data["conversion_rates"]
            exchange_rate = rates.get(to_currency)
            if exchange_rate:
                # Convert amount to Decimal for precision
                converted_amount = Decimal(amount) * Decimal(str(exchange_rate))
                return converted_amount.quantize(Decimal('0.01'))  # Round to 2 decimal places
        else:
            return amount  # Return the original amount if API call fails
    except Exception as e:
        print("Currency Conversion Error:", e)
        return amount

import requests
from django.conf import settings

def get_available_currencies():
    """
    Fetches available currencies from ExchangeRate-API.
    """
    base_url = settings.EXCHANGE_RATE_BASE_URL
    try:
        response = requests.get(base_url)
        data = response.json()
        if response.status_code == 200 and "conversion_rates" in data:
            currencies = list(data["conversion_rates"].keys())
            return currencies
        else:
            return ["USD", "INR", "EUR", "GBP", "AUD"]  # Default options if API call fails
    except Exception as e:
        print("Currency Fetch Error:", e)
        return ["USD", "INR", "EUR", "GBP", "AUD"]
