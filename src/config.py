"""
MarketSherlock Configuration Module
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
ARCHIVES_DIR = ROOT_DIR / "archives"
WEB_DIR = ROOT_DIR / "web"
LATEST_MD_PATH = ROOT_DIR / "LATEST.md"
README_MD_PATH = ROOT_DIR / "README.md"
INDEX_HTML_PATH = WEB_DIR / "index.html"
HISTORY_FILE = DATA_DIR / "history.json"

# Load environment variables
load_dotenv(ROOT_DIR / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# AI Models (Primary and Fallbacks)
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest"
]

# Market Snapshot Tickers (yfinance)
MARKET_TICKERS = {
    "SET Index": "^SET.BK",
    "S&P 500": "^GSPC",
    "US 10Y Yield": "^TNX",
    "Crude Oil (WTI)": "CL=F",
    "Gold (Spot/Futures)": "GC=F",
    "USD/THB": "THB=X"
}

# Whitelist of Trusted Sources
TRUSTED_SOURCES = [
    "Bloomberg",
    "Reuters",
    "Financial Times",
    "The Wall Street Journal",
    "กรุงเทพธุรกิจ (Krungthep Turakij)",
    "ธนาคารแห่งประเทศไทย (BOT)",
    "สำนักงานคณะกรรมการกำกับหลักทรัพย์และตลาดหลักทรัพย์ (ก.ล.ต. / SEC)",
    "ตลาดหลักทรัพย์แห่งประเทศไทย (SET)",
    "สำนักงานสภาพัฒนาการเศรษฐกิจและสังคมแห่งชาติ (สภาพัฒน์ / NESDC)",
    "สำนักงานคณะกรรมการส่งเสริมการลงทุน (BOI)",
    "The Standard Wealth",
    "InfoQuest",
    "Bangkok Post"
]
