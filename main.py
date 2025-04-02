from fastapi import FastAPI
import ccxt
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Crypto Signal API is running."}

@app.get("/signal")
def get_signal(pair: str = "BTC/USDT", currency: str = "USD"):
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='15m', limit=100)
        closes = [x[4] for x in ohlcv]
        df = pd.DataFrame(closes, columns=["close"])

        # Indicators
        ema_fast = EMAIndicator(df["close"], window=12).ema_indicator()
        ema_slow = EMAIndicator(df["close"], window=26).ema_indicator()
        rsi = RSIIndicator(df["close"], window=14).rsi()
        bb = BollingerBands(df["close"])
        current_price = df["close"].iloc[-1]

        # Signal Logic
        bullish = ema_fast.iloc[-1] > ema_slow.iloc[-1] and rsi.iloc[-1] < 70
        bearish = ema_fast.iloc[-1] < ema_slow.iloc[-1] and rsi.iloc[-1] > 30

        trend = "bullish" if bullish else "bearish" if bearish else "neutral"

        entry = round(current_price, 2)
        stop_loss = round(entry * 0.98, 2)
        take_profit = round(entry * 1.04, 2)

        return {
            "pair": pair,
            "currency": currency,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "trend": trend,
            "rsi": round(rsi.iloc[-1], 2),
            "ema_fast": round(ema_fast.iloc[-1], 2),
            "ema_slow": round(ema_slow.iloc[-1], 2)
        }

    except Exception as e:
        return {"error": str(e)}