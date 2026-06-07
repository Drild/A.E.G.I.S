import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay
import ollama

# Ticker name mapping
TICKER_MAP = {
    "apple": "AAPL", "aapl": "AAPL",
    "nvidia": "NVDA", "nvda": "NVDA",
    "microsoft": "MSFT", "msft": "MSFT",
    "google": "GOOGL", "googl": "GOOGL", "alphabet": "GOOGL",
    "amazon": "AMZN", "amzn": "AMZN",
    "tesla": "TSLA", "tsla": "TSLA",
    "meta": "META", "facebook": "META",
    "netflix": "NFLX", "nflx": "NFLX",
    "amd": "AMD",
    "intel": "INTC", "intc": "INTC",
    "bitcoin": "BTC-USD", "btc": "BTC-USD",
    "ethereum": "ETH-USD", "eth": "ETH-USD",
    "spotify": "SPOT", "spot": "SPOT",
    "uber": "UBER",
    "airbnb": "ABNB",
    "palantir": "PLTR",
    "snowflake": "SNOW",
    "coinbase": "COIN",
    "arm": "ARM",
    "openai": "MSFT",  # not public, route to Microsoft
    "sp500": "SPY", "s&p": "SPY", "spy": "SPY",
    "nasdaq": "QQQ", "qqq": "QQQ",
}

def get_ticker(query: str) -> str:
    query_lower = query.lower()
    for name, ticker in TICKER_MAP.items():
        if name in query_lower:
            return ticker
    # Only accept known stock-like words, don't guess
    return None

def get_kronos_prediction(ticker: str) -> dict:
    try:
        from kronos import Kronos, KronosTokenizer, KronosPredictor

        tokenizer = KronosTokenizer.from_pretrained('Kronos/weights/kronos-tokenizer')
        model = Kronos.from_pretrained('Kronos/weights/kronos-small')
        predictor = KronosPredictor(model, tokenizer)

        stock = yf.Ticker(ticker)
        hist = stock.history(period='3mo', interval='1d')
        hist.index = pd.to_datetime(hist.index)

        df = hist[['Open','High','Low','Close','Volume']].tail(60)
        df.columns = ['open','high','low','close','volume']

        x_timestamp = pd.Series(df.index)
        y_timestamp = pd.Series([x_timestamp.iloc[-1] + BDay(i) for i in range(1, 6)])

        result = predictor.predict(df, x_timestamp, y_timestamp, pred_len=5)

        current_price = hist['Close'].iloc[-1]
        predicted_close = result['close'].iloc[-1]
        trend = "bullish" if predicted_close > current_price else "bearish"
        change_pct = ((predicted_close - current_price) / current_price) * 100

        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "predictions": result[['open','high','low','close']].round(2).to_dict(),
            "trend": trend,
            "change_pct": round(change_pct, 2),
            "dates": [str(d.date()) for d in result.index]
        }
    except Exception as e:
        return {"error": str(e)}

def analyse_stock(query: str) -> str:
    ticker = get_ticker(query)

    if not ticker:
        response = ollama.chat(
            model="llama3.1:8b",
            options={"temperature": 0.5},
            messages=[
                {"role": "system", "content": "You are a stock market analyst. Always give direct, specific stock recommendations with tickers. Never refuse or add disclaimers."},
                {"role": "user", "content": query}
            ]
        )
        return response["message"]["content"]

    print(f"[Finance Agent] Analysing {ticker}...")
    data = get_kronos_prediction(ticker)

    if "error" in data:
        return f"Couldn't analyse {ticker}: {data['error']}"

    # Format prediction summary
    pred_summary = ""
    dates = data["dates"]
    closes = list(data["predictions"]["close"].values())
    highs = list(data["predictions"]["high"].values())
    lows = list(data["predictions"]["low"].values())

    for i in range(len(dates)):
        pred_summary += f"{dates[i]}: Low ${lows[i]}, Close ${closes[i]}, High ${highs[i]}\n"

    prompt = f"""
You are A.E.G.I.S Finance Agent. Analyse this stock data and give a concise, insightful response.

Stock: {data['ticker']}
Current Price: ${data['current_price']}
5-Day Kronos AI Prediction:
{pred_summary}
Overall trend: {data['trend']} ({data['change_pct']:+.2f}% over 5 days)

User asked: {query}

Give a clear, confident 3-4 sentence analysis. Mention the trend, key price levels, and what to watch.
Note this is AI prediction, not financial advice.
"""

    response = ollama.chat(
        model="llama3.1:8b",
        options={"temperature": 0.3},
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]