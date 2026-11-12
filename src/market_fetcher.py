"""
Market Fetcher - Fetches real-time market data using yfinance
"""
from typing import Dict, Any, List
import yfinance as yf
from src.config import MARKET_TICKERS

def fetch_single_ticker(name: str, symbol: str) -> Dict[str, Any]:
    """Fetch recent price data for a single symbol with fallback handling."""
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="5d")
        if hist.empty or len(hist["Close"].dropna()) == 0:
            return {
                "name": name,
                "symbol": symbol,
                "price": None,
                "change": 0.0,
                "percent_change": 0.0,
                "status": "⚪",
                "formatted": "N/A"
            }
        
        close_series = hist["Close"].dropna()
        last_price = float(close_series.iloc[-1])
        prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else last_price
        
        change = last_price - prev_price
        pct_change = (change / prev_price * 100) if prev_price != 0 else 0.0
        
        # Determine status emoji
        if pct_change > 0.05:
            status = "🟢"
        elif pct_change < -0.05:
            status = "🔴"
        else:
            status = "⚪"
            
        unit = "%" if symbol == "^TNX" else ("THB" if symbol == "THB=X" else "")
        price_display = f"{last_price:.2f}{unit}" if unit else f"{last_price:,.2f}"
        
        return {
            "name": name,
            "symbol": symbol,
            "price": last_price,
            "prev_price": prev_price,
            "change": change,
            "percent_change": pct_change,
            "status": status,
            "price_display": price_display,
            "change_display": f"{change:+.2f} ({pct_change:+.2f}%)"
        }
    except Exception as e:
        return {
            "name": name,
            "symbol": symbol,
            "price": None,
            "change": 0.0,
            "percent_change": 0.0,
            "status": "⚠️",
            "price_display": "Error",
            "change_display": str(e)[:25]
        }

def get_market_snapshot() -> Dict[str, Any]:
    """Fetch all indicators in MARKET_TICKERS and return formatted data."""
    results: List[Dict[str, Any]] = []
    for name, symbol in MARKET_TICKERS.items():
        data = fetch_single_ticker(name, symbol)
        results.append(data)
    
    # Generate Markdown Table
    md_lines = [
        "| สินทรัพย์ / ดัชนี | สัญลักษณ์ | ราคาล่าสุด | การเปลี่ยนแปลง | ทิศทาง |",
        "| :--- | :--- | :---: | :---: | :---: |"
    ]
    for r in results:
        md_lines.append(f"| **{r['name']}** | `{r['symbol']}` | {r['price_display']} | {r['change_display']} | {r['status']} |")
    
    markdown_table = "\n".join(md_lines)
    return {
        "items": results,
        "markdown_table": markdown_table
    }

if __name__ == "__main__":
    snapshot = get_market_snapshot()
    print(snapshot["markdown_table"])
