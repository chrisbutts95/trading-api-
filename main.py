from fastapi import FastAPI
import requests

app = FastAPI()

OANDA_API_KEY = "PASTE_YOURS"
ACCOUNT_ID = "PASTE_YOURS"

def get_candles():
    url = "https://api-fxpractice.oanda.com/v3/instruments/EUR_USD/candles"
    
    headers = {
        "Authorization": f"Bearer {OANDA_API_KEY}"
    }

    params = {
        "granularity": "M5",
        "count": 50
    }

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    candles = []
    for c in data["candles"]:
        candles.append({
            "open": float(c["mid"]["o"]),
            "close": float(c["mid"]["c"]),
            "high": float(c["mid"]["h"]),
            "low": float(c["mid"]["l"])
        })

    return candles

def analyze_market(data):
    first = data[0]

    bias = "BUY" if first["close"] > first["open"] else "SELL"
    price = data[-1]["close"]

    zone_low = min(d["low"] for d in data[-10:])
    zone_high = max(d["high"] for d in data[-10:])

    if bias == "BUY" and price <= zone_low:
        return {"valid": True, "bias": bias, "entry": price, "sl": price - 0.002, "tp": price + 0.006}
    
    if bias == "SELL" and price >= zone_high:
        return {"valid": True, "bias": bias, "entry": price, "sl": price + 0.002, "tp": price - 0.006}

    return {"valid": False, "bias": bias}

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/signal")
def signal():
    data = get_candles()
    return analyze_market(data)
