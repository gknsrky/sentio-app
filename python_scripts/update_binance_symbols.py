import requests
import json
import os

def update_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    symbols = response.json()["symbols"]

    spot_symbols = [
    s["symbol"]
    for s in symbols
    if s["status"] == "TRADING"
    and s["isSpotTradingAllowed"]
    and s["symbol"].endswith("USDT")
]

    output_path = os.path.join(os.path.dirname(__file__), "../data/binance_symbols.json")
    with open(output_path, "w") as f:
        json.dump(spot_symbols, f, indent=2)

    print(f"{len(spot_symbols)} adet coin listesi güncellendi.")

if __name__ == "__main__":
    update_symbols()
