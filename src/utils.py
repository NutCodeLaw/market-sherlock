"""
Utility functions for MarketSherlock (Timezone, Date formatting, Markdown cleanup)
"""
from datetime import datetime, timezone, timedelta

# Thai timezone UTC+7
BANGKOK_TZ = timezone(timedelta(hours=7))

THAI_MONTHS = [
    "",
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def get_now_bangkok() -> datetime:
    """Return current datetime in Asia/Bangkok."""
    return datetime.now(BANGKOK_TZ)

def format_thai_date(dt: datetime = None) -> str:
    """Format datetime into Thai date string: '12 พฤศจิกายน 2569'."""
    if dt is None:
        dt = get_now_bangkok()
    thai_year = dt.year + 543
    month_name = THAI_MONTHS[dt.month]
    return f"{dt.day} {month_name} {thai_year}"

def get_iso_date(dt: datetime = None) -> str:
    """Return ISO format YYYY-MM-DD."""
    if dt is None:
        dt = get_now_bangkok()
    return dt.strftime("%Y-%m-%d")
