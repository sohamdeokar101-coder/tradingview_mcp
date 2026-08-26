import asyncio
import pandas as pd
from fastmcp import FastMCP
from tvDatafeed import TvDatafeed, Interval
from finta import TA
from typing import List, Dict, Any

# 1. Initialize
mcp = FastMCP("TradingViewPro")
tv = TvDatafeed()

INTERVAL_MAP = {
    "1m": Interval.in_1_minute,
    "5m": Interval.in_5_minute,
    "15m": Interval.in_15_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
}

# --- TOOL 1: Search ---
@mcp.tool()
async def find_symbols(text: str) -> List[Dict[str, str]]:
    """Search for a symbol/ticker on TradingView to get the correct symbol and exchange."""
    results = tv.search_symbol(text)
    if not results:
        return []
    return [{"symbol": r['symbol'], "exchange": r['exchange'], "description": r['description']} for r in results[:5]]

# --- TOOL 2: Live Price ---
@mcp.tool()
async def get_live_quote(symbol: str, exchange: str = "NASDAQ") -> Dict[str, Any]:
    """Fetches the absolute current price, the day's High/Low, and timestamp."""
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_1_minute, n_bars=1)
    if data is None or data.empty:
        return {"error": f"Could not find price for {exchange}:{symbol}"}
    
    return {
        "symbol": symbol,
        "current_price": round(data.iloc[-1]['close'], 2),
        "high": round(data.iloc[-1]['high'], 2),
        "low": round(data.iloc[-1]['low'], 2),
        "timestamp": str(data.index[-1])
    }

# --- TOOL 3: Technical Analysis ---
@mcp.tool()
async def get_technical_analysis(symbol: str, exchange: str, interval: str = "1h") -> Dict[str, Any]:
    """Calculates RSI, SMA 20/50, and EMA for a symbol to determine market conditions."""
    selected_interval = INTERVAL_MAP.get(interval, Interval.in_1_hour)
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=selected_interval, n_bars=100)
    
    if data is None or data.empty:
        return {"error": "No data retrieved"}

    data.columns = [x.lower() for x in data.columns]
    
    rsi = TA.RSI(data, 14).iloc[-1]
    sma_20 = TA.SMA(data, 20).iloc[-1]
    sma_50 = TA.SMA(data, 50).iloc[-1]
    ema_50 = TA.EMA(data, 50).iloc[-1]
    
    return {
        "symbol": symbol,
        "rsi": round(rsi, 2),
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "ema_50": round(ema_50, 2),
        "condition": "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
    }

# --- TOOL 4: Trend Signal ---
@mcp.tool()
async def get_trend_signal(symbol: str, exchange: str) -> str:
    """Analyzes the trend using SMA crossover logic (20-period vs 50-period)."""
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_1_hour, n_bars=100)
    if data is None or data.empty: return "Data unavailable."
    
    data.columns = [x.lower() for x in data.columns]
    current_sma20 = TA.SMA(data, 20).iloc[-1]
    current_sma50 = TA.SMA(data, 50).iloc[-1]
    
    status = "BULLISH" if current_sma20 > current_sma50 else "BEARISH"
    return f"{status}: The 20-period SMA (${current_sma20:.2f}) is {'above' if status == 'BULLISH' else 'below'} the 50-period SMA (${current_sma50:.2f})."

# --- TOOL 5: Volume Prediction ---
@mcp.tool()
async def predict_trend_with_volume(symbol: str, exchange: str) -> Dict[str, Any]:
    """Uses Volume-Price analysis to predict if the current trend is likely to continue."""
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=1000)
    if data is None or data.empty: return {"error": "Data unavailable"}
    
    data.columns = [x.lower() for x in data.columns]
    current_vol = data.iloc[-1]['volume']
    avg_vol = data['volume'].tail(20).mean()
    vol_ratio = current_vol / avg_vol
    price_change = (data.iloc[-1]['close'] - data.iloc[-2]['close'])
    
    if price_change > 0 and vol_ratio > 1.2:
        prediction = "Strong Bullish Continuation (High Volume Breakout)"
    elif price_change > 0 and vol_ratio < 0.8:
        prediction = "Weak Bullish (Price up but Volume fading - possible reversal)"
    elif price_change < 0 and vol_ratio > 1.2:
        prediction = "Strong Bearish (High Volume Selling)"
    else:
        prediction = "Neutral / Consolidation"

    return {
        "symbol": symbol,
        "volume_vs_avg": f"{vol_ratio:.2f}x",
        "trend_prediction": prediction,
        "confidence": "High" if vol_ratio > 1.5 else "Medium"
    }

# --- TOOL 6: Market Overview ---
@mcp.tool()
async def get_market_overview() -> Dict[str, str]:
    """Provides a quick snapshot of major global markets (S&P 500, Gold, BTC)."""
    major_tickers = [
        {"symbol": "SPY", "exchange": "AMEX", "name": "S&P 500"},
        {"symbol": "GOLD", "exchange": "TVC", "name": "Gold"},
        {"symbol": "BTCUSD", "exchange": "BINANCE", "name": "Bitcoin"}
    ]
    overview = {}
    for item in major_tickers:
        try:
            data = tv.get_hist(item['symbol'], item['exchange'], n_bars=2)
            if data is not None:
                close = data.iloc[-1]['close']
                prev_close = data.iloc[-2]['close']
                pct_change = ((close - prev_close) / prev_close) * 100
                overview[item['name']] = f"${close:,.2f} ({pct_change:+.2f}%)"
        except:
            overview[item['name']] = "Data Unavailable"
    return overview

# --- TOOL 7: Data Export ---
@mcp.tool()
async def export_historical_data(symbol: str, exchange: str, n_bars: int = 1000) -> str:
    """Downloads data and exports to a CSV file on your local machine."""
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_1_hour, n_bars=n_bars)
    if data is None or data.empty: return "No data to export."
    filename = f"{symbol}_export.csv"
    data.to_csv(filename)
    return f"Successfully exported {len(data)} bars to {filename}"

if __name__ == "__main__":
    mcp.run()