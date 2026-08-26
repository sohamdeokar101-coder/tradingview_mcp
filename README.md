# TradingView Pro MCP Server 🚀📈

A custom **Model Context Protocol (MCP)** server built with **FastMCP** that connects AI agents (like Antigravity CLI, Claude Desktop, Cursor) directly to **TradingView** data via `tvDatafeed` and `finta`.

---

## 🌟 Features
* **Symbol Search (`find_symbols`):** Search for tickers and exchange mappings on TradingView.
* **Live Quotes (`get_live_quote`):** Fetch real-time prices, day highs, day lows, and timestamps.
* **Technical Analysis (`get_technical_analysis`):** Calculate RSI (14), SMA (20/50), and EMA (50).
* **Trend Signals (`get_trend_signal`):** Analyze market trends using moving average crossover logic.
* **Volume Prediction (`predict_trend_with_volume`):** Evaluate volume-price relationships to predict breakouts or reversals.
* **Market Overview (`get_market_overview`):** Snapshot global benchmark assets (S&P 500, Gold, Bitcoin).
* **Data Export (`export_historical_data`):** Download historical market data directly to local CSV files.

---

## 💻 Sample Outputs & Agent Interaction

### 1. Live Quote (`get_live_quote`)
> **Query:** `> Can you get the live quote for AAPL on NASDAQ?`

```text
Metric          │ Value
────────────────┼──────────────────────
Symbol          │ AAPL
Exchange        │ NASDAQ
Current Price   │ $312.45
Day High        │ $312.70
Day Low         │ $312.38
Timestamp       │ 2026-08-26 16:55:00


2. Technical Analysis & RSI (get_technical_analysis + get_trend_signal)
Query: > Calculate the technical analysis and RSI for BTCUSD on BINANCE

### Technical Indicators

Indicator       │ Value      │ Interpretation
────────────────┼────────────┼────────────────────────────────────────────
Current Price   │ $77,785.30 │ Last traded price
RSI (14-period) │ 35.77      │ Neutral (Approaching oversold territory < 30)
SMA 20          │ $78,644.45 │ Short-term moving average
SMA 50          │ $79,084.27 │ Medium-term moving average
EMA 50          │ $78,710.37 │ Exponential moving average

### Summary & Trend Analysis

• Market Condition: Neutral
• Trend Signal: Bearish — The 20-period SMA ($78,644.45) remains below the 50-period SMA ($79,084.27), with the current price ($77,785.30) trading below both moving averages.
• Momentum: RSI at 35.77 reflects selling momentum without yet reaching oversold levels.

 
## Installation & Setup

1. Clone or copy the project files into your local directory.
2. Install the required dependencies:
   ```bash
   pip install fastmcp pandas tvDatafeed finta
   ```bash
   pip install fastmcp pandas tvDatafeed finta


Run the MCP server manually or register it under your AI assistant's MCP configuration (mcp_config.json):
{
  "mcpServers": {
    "TradingViewPro": {
      "command": "/usr/local/bin/python3",
      "args": [
        "/Volumes/External SSD/Equity Analysis Research Lab University course/Week8/tradingview_mcp.py"
      ]
    }
  }
}


Usage
Start your server script or let your MCP-compatible client (like Antigravity CLI or Claude Desktop) manage it automatically via stdio transport.


















   
