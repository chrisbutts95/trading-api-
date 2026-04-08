from fastapi import FastAPI
import requests
import os

app = FastAPI()

# Get API key from Railway environment variables
OANDA_API_KEY = os.getenv("OANDA_API_KEY")


# 🔹 GET MARKET DATA FROM OANDA
def get_candles():
    if not OANDA_API_KEY:
        return []

    url = "https://api-fxpractice.oanda.com/v3/instruments/EUR_USD/candles"

    headers = {
        "Authorization": f"Bearer {OANDA_API_KEY}"
    }

    params = {
        "granularity": "M5",
        "count": 50
    }

    try:
        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            return []

        data = res.json()

        candles = []
        for c in data.get("candles", []):
            candles.append({
                "open": float(c["mid"]["o"]),
                "close": float(c["mid"]["c"]),
                "high": float(c["mid"]["h"]),
                "low": float(c["mid"]["l"])
            })

        return candles

    except:
        return []


# 🔹 YOUR TRADING LOGIC
def analyze_market(data):
    try:
        first = data[0]

        bias = "BUY" if first["close"] > first["open"] else "SELL"
        price = data[-1]["close"]

        zone_low = min(d["low"] for d in data[-10:])
        zone_high = max(d["high"] for d in data[-10:])

        if bias == "BUY" and price <= zone_low:
            return {
                "valid": True,
                "bias": bias,
                "entry": price,
                "sl": price - 0.002,
                "tp": price + 0.006
            }

        if bias == "SELL" and price >= zone_high:
            return {
                "valid": True,
                "bias": bias,
                "entry": price,
                "sl": price + 0.002,
                "tp": price - 0.006
            }

        return {"valid": False, "bias": bias}

    except Exception as e:
        return {"valid": False, "error": str(e)}


# 🔹 ROOT ROUTE (HEALTH CHECK)
@app.get("/")
def home():
    return {"status": "running"}


# 🔹 SIGNAL ROUTE (MAIN FEATURE)
@app.get("/signal")
def signal():
    try:
        data = get_candles()

        if not data or len(data) < 10:
            return {"valid": False, "error": "No market data"}

        return analyze_market(data)

    except Exception as e:
        return {"valid": False, "error": str(e)}