"""
Holiday Guard - Thai Stock Market (SET) Trading Calendar & Automatic Holiday Rollover
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from src.utils import get_now_bangkok

# Official Stock Exchange of Thailand (SET) Holidays (2026-2027)
# Source: The Stock Exchange of Thailand (set.or.th) / Bank of Thailand
SET_OFFICIAL_HOLIDAYS: Dict[str, str] = {
    # --- 2026 ---
    "2026-01-01": "วันขึ้นปีใหม่ (New Year's Day)",
    "2026-01-02": "วันหยุดทำการเพิ่มเป็นกรณีพิเศษ (Additional Special Holiday)",
    "2026-03-03": "วันมาฆบูชา (Makha Bucha Day)",
    "2026-04-06": "วันพระบาทสมเด็จพระพุทธยอดฟ้าจุฬาโลกมหาราช และวันที่ระลึกมหาจักรีบรมราชวงศ์ (Chakri Memorial Day)",
    "2026-04-13": "วันสงกรานต์ (Songkran Festival)",
    "2026-04-14": "วันสงกรานต์ (Songkran Festival)",
    "2026-04-15": "วันสงกรานต์ (Songkran Festival)",
    "2026-05-01": "วันแรงงานแห่งชาติ (National Labour Day)",
    "2026-05-04": "วันฉัตรมงคล (Coronation Day)",
    "2026-06-01": "ชดเชยวันวิสาขบูชา (Substitution for Visakha Bucha Day)",
    "2026-06-03": "วันเฉลิมพระชนมพรรษาสมเด็จพระนางเจ้าฯ พระบรมราชินี (H.M. Queen's Birthday)",
    "2026-07-28": "วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว (H.M. King's Birthday)",
    "2026-07-29": "วันอาสาฬหบูชา (Asarnha Bucha Day)",
    "2026-08-12": "วันเฉลิมพระชนมพรรษาสมเด็จพระบรมราชชนนีพันปีหลวง และวันแม่แห่งชาติ (Mother's Day)",
    "2026-10-13": "วันนวมินทรมหาราช (H.M. King Bhumibol Adulyadej Memorial Day)",
    "2026-10-16": "วันหยุดทำการเพิ่มเป็นกรณีพิเศษ (Additional Special Holiday)",
    "2026-10-23": "วันปิยมหาราช (Chulalongkorn Day)",
    "2026-12-07": "ชดเชยวันชาติ และวันพ่อแห่งชาติ (Substitution for National Day & Father's Day)",
    "2026-12-10": "วันรัฐธรรมนูญ (Constitution Day)",
    "2026-12-16": "วันหยุดทำการเพิ่มเป็นกรณีพิเศษ (Additional Special Holiday)",
    "2026-12-31": "วันสิ้นปี (New Year's Eve)",

    # --- 2027 ---
    "2027-01-01": "วันขึ้นปีใหม่ (New Year's Day)",
    "2027-02-22": "ชดเชยวันมาฆบูชา (Substitution for Makha Bucha Day)",
    "2027-04-06": "วันจักรี (Chakri Memorial Day)",
    "2027-04-13": "วันสงกรานต์ (Songkran Festival)",
    "2027-04-14": "วันสงกรานต์ (Songkran Festival)",
    "2027-04-15": "วันสงกรานต์ (Songkran Festival)",
    "2027-05-03": "ชดเชยวันแรงงานแห่งชาติ (Substitution for National Labour Day)",
    "2027-05-04": "วันฉัตรมงคล (Coronation Day)",
    "2027-05-20": "วันวิสาขบูชา (Visakha Bucha Day)",
    "2027-06-03": "วันเฉลิมพระชนมพรรษาสมเด็จพระนางเจ้าฯ พระบรมราชินี (H.M. Queen's Birthday)",
    "2027-07-19": "ชดเชยวันอาสาฬหบูชา (Substitution for Asarnha Bucha Day)",
    "2027-07-28": "วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว (H.M. King's Birthday)",
    "2027-08-12": "วันแม่แห่งชาติ (Mother's Day)",
    "2027-10-13": "วันนวมินทรมหาราช (H.M. King Bhumibol Adulyadej Memorial Day)",
    "2027-10-25": "ชดเชยวันปิยมหาราช (Substitution for Chulalongkorn Day)",
    "2027-12-06": "ชดเชยวันชาติ และวันพ่อแห่งชาติ (Substitution for National Day & Father's Day)",
    "2027-12-10": "วันรัฐธรรมนูญ (Constitution Day)",
    "2027-12-31": "วันสิ้นปี (New Year's Eve)",
}

# Fixed annual Thai bank/SET holidays (month, day) for fallback beyond official table years
FIXED_ANNUAL_SET_HOLIDAYS = {
    (1, 1): "วันขึ้นปีใหม่ (New Year's Day)",
    (4, 6): "วันจักรี (Chakri Memorial Day)",
    (4, 13): "วันสงกรานต์ (Songkran Festival)",
    (4, 14): "วันสงกรานต์ (Songkran Festival)",
    (4, 15): "วันสงกรานต์ (Songkran Festival)",
    (5, 1): "วันแรงงานแห่งชาติ (National Labour Day)",
    (5, 4): "วันฉัตรมงคล (Coronation Day)",
    (6, 3): "วันเฉลิมพระชนมพรรษาสมเด็จพระนางเจ้าฯ พระบรมราชินี",
    (7, 28): "วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว",
    (8, 12): "วันแม่แห่งชาติ (Mother's Day)",
    (10, 13): "วันนวมินทรมหาราช",
    (10, 23): "วันปิยมหาราช (Chulalongkorn Day)",
    (12, 5): "วันชาติ และวันพ่อแห่งชาติ",
    (12, 10): "วันรัฐธรรมนูญ (Constitution Day)",
    (12, 31): "วันสิ้นปี (New Year's Eve)",
}


def _build_substituted_holidays_for_year(year: int) -> Dict[str, str]:
    """Generate fixed + weekend-substituted SET holidays for years beyond 2027."""
    result: Dict[str, str] = {}
    for (month, day), label in sorted(FIXED_ANNUAL_SET_HOLIDAYS.items()):
        dt = datetime(year, month, day)
        iso = dt.strftime("%Y-%m-%d")
        if dt.weekday() < 5 and iso not in result:
            result[iso] = label
        else:
            # Find next weekday not already occupied by a fixed holiday
            candidate = dt + timedelta(days=1)
            while (
                candidate.weekday() >= 5
                or candidate.strftime("%Y-%m-%d") in result
                or (candidate.month, candidate.day) in FIXED_ANNUAL_SET_HOLIDAYS
            ):
                candidate += timedelta(days=1)
            result[candidate.strftime("%Y-%m-%d")] = f"ชดเชย{label}"
    return result


def get_set_non_trading_reason(dt: Optional[datetime] = None) -> Optional[str]:
    """Return non-trading reason if `dt` (Asia/Bangkok) is a weekend or SET holiday, else None."""
    if dt is None:
        dt = get_now_bangkok()

    if dt.weekday() >= 5:
        return "วันหยุดสุดสัปดาห์ (เสาร์–อาทิตย์)"

    iso_date = dt.strftime("%Y-%m-%d")
    if iso_date in SET_OFFICIAL_HOLIDAYS:
        return SET_OFFICIAL_HOLIDAYS[iso_date]

    # Fallback calendar for 2028+ until official SET table is updated
    if dt.year > 2027:
        fallback_holidays = _build_substituted_holidays_for_year(dt.year)
        if iso_date in fallback_holidays:
            return fallback_holidays[iso_date]

    return None


def is_set_trading_day(dt: Optional[datetime] = None) -> bool:
    """Return True if the Stock Exchange of Thailand (SET) is open on `dt`."""
    return get_set_non_trading_reason(dt) is None


def get_next_set_trading_day(dt: Optional[datetime] = None) -> datetime:
    """Return the next open SET trading day strictly after `dt`."""
    if dt is None:
        dt = get_now_bangkok()
    candidate = dt + timedelta(days=1)
    while not is_set_trading_day(candidate):
        candidate += timedelta(days=1)
    return candidate
