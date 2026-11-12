"""
State Manager - Supports Weekly reporting cycles and automatic holiday rollover
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from src.config import HISTORY_FILE
from src.utils import get_now_bangkok

def load_history() -> List[Dict[str, Any]]:
    """Load history records from history.json."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_history(records: List[Dict[str, Any]]) -> None:
    """Save history records to history.json."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records[-30:], f, ensure_ascii=False, indent=2)

def get_current_week_identifier(dt: datetime = None) -> str:
    """Return Year-Week string e.g. '2026-W46'."""
    if dt is None:
        dt = get_now_bangkok()
    year, week_num, _ = dt.isocalendar()
    return f"{year}-W{week_num:02d}"

def is_current_week_already_reported() -> bool:
    """Check if a weekly report for this calendar week has already been generated."""
    current_week = get_current_week_identifier()
    history = load_history()
    for entry in history:
        if entry.get("week_id") == current_week:
            return True
    return False

def append_weekly_topics(week_id: str, date_str: str, topics: List[Dict[str, Any]]) -> None:
    """Record this week's completed report."""
    history = load_history()
    history = [h for h in history if h.get("week_id") != week_id]
    history.append({
        "week_id": week_id,
        "date": date_str,
        "topics": topics,
        "updated_at": datetime.now().isoformat()
    })
    save_history(history)

def get_recent_history_context(days: int = 14) -> str:
    """Format past weekly topics to maintain analytical continuity."""
    history = load_history()
    if not history:
        return "ไม่มีประวัติการรายงานรายสัปดาห์ก่อนหน้า (รายงานสัปดาห์แรก)"

    entries = []
    for entry in history[-4:]:
        w_id = entry.get("week_id", "")
        d_str = entry.get("date", "")
        topic_list = entry.get("topics", [])
        if not topic_list:
            continue
        items_summary = [f"- {t.get('title', '')}" for t in topic_list if isinstance(t, dict)]
        entries.append(f"สัปดาห์ {w_id} ({d_str}):\n" + "\n".join(items_summary))
        
    return "\n\n".join(entries) if entries else "ไม่มีประวัติการรายงานในช่วง 14 วันที่ผ่านมา"
