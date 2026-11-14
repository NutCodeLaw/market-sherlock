"""
Market Fetcher - Weekly Candlestick (1W Timeframe) Performance & Snapshot
"""
from typing import Dict, Any, List
import yfinance as yf
from src.config import MARKET_TICKERS

def fetch_weekly_ticker(name: str, symbol: str) -> Dict[str, Any]:
    """Fetch 1-Week candlestick performance and 1W High/Low range."""
    try:
        t = yf.Ticker(symbol)
        # Fetch 1 month of daily data to compute rolling 5 trading days (1 full week)
        hist = t.history(period="1mo")
        if hist.empty:
            last_price = float(t.fast_info.get("last_price") or 0)
            if last_price == 0:
                return {
                    "name": name,
                    "symbol": symbol,
                    "price": None,
                    "change": 0.0,
                    "percent_change": 0.0,
                    "week_high": 0.0,
                    "week_low": 0.0,
                    "status": "⚪",
                    "price_display": "N/A",
                    "change_display": "N/A",
                    "range_display": "N/A"
                }
            prev_week_price = float(t.fast_info.get("previous_close") or last_price)
            week_high = max(last_price, prev_week_price)
            week_low = min(last_price, prev_week_price)
        else:
            closes = hist["Close"].dropna()
            highs = hist["High"].dropna()
            lows = hist["Low"].dropna()
            if len(closes) < 2:
                fallback_close = float(closes.iloc[-1]) if not closes.empty else 0.0
                last_price = float(t.fast_info.get("last_price") or fallback_close)
                prev_week_price = float(t.fast_info.get("previous_close") or last_price)
                week_high = max(last_price, prev_week_price)
                week_low = min(last_price, prev_week_price)
            else:
                last_price = float(closes.iloc[-1])
                prev_week_price = float(closes.iloc[-6]) if len(closes) >= 6 else float(closes.iloc[0])
                week_high = float(highs.tail(5).max())
                week_low = float(lows.tail(5).min())
            
        change_1w = last_price - prev_week_price
        pct_change_1w = (change_1w / prev_week_price * 100) if prev_week_price != 0 else 0.0
        
        # Weekly candlestick bias
        if pct_change_1w > 0.5:
            status = "🟢"
        elif pct_change_1w < -0.5:
            status = "🔴"
        else:
            status = "⚪"
            
        unit = "%" if symbol == "^TNX" else ("THB" if symbol == "THB=X" else "")
        price_display = f"{last_price:.2f}{unit}" if unit else f"{last_price:,.2f}"
        
        return {
            "name": name,
            "symbol": symbol,
            "price": last_price,
            "prev_week_price": prev_week_price,
            "change": change_1w,
            "percent_change": pct_change_1w,
            "week_high": week_high,
            "week_low": week_low,
            "status": status,
            "price_display": price_display,
            "change_display": f"{change_1w:+.2f} ({pct_change_1w:+.2f}%)",
            "range_display": f"{week_low:,.2f} - {week_high:,.2f}" if unit == "" else f"{week_low:.2f}{unit} - {week_high:.2f}{unit}"
        }
    except Exception as e:
        return {
            "name": name,
            "symbol": symbol,
            "price": None,
            "change": 0.0,
            "percent_change": 0.0,
            "week_high": 0.0,
            "week_low": 0.0,
            "status": "⚠️",
            "price_display": "Error",
            "change_display": str(e)[:25],
            "range_display": "N/A"
        }

def get_market_snapshot() -> Dict[str, Any]:
    """Fetch 1-Week indicators and return formatted weekly table."""
    results: List[Dict[str, Any]] = []
    for name, symbol in MARKET_TICKERS.items():
        data = fetch_weekly_ticker(name, symbol)
        results.append(data)
    
    # Generate Weekly Markdown Table
    md_lines = [
        "| สินทรัพย์ / ดัชนี | สัญลักษณ์ | ราคาปิดล่าสุด | ผลตอบแทนรอบสัปดาห์ (1W) | กรอบสัปดาห์ (1W High-Low) | สัญญาณแท่งเทียน |",
        "| :--- | :--- | :---: | :---: | :---: | :---: |"
    ]
    for r in results:
        md_lines.append(f"| **{r['name']}** | `{r['symbol']}` | {r['price_display']} | {r['change_display']} | `{r['range_display']}` | {r['status']} |")
    
    markdown_table = "\n".join(md_lines)
    return {
        "items": results,
        "markdown_table": markdown_table
    }

if __name__ == "__main__":
    snapshot = get_market_snapshot()
    print(snapshot["markdown_table"])
