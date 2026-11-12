"""
State Manager - Prevents duplicate news and tracks continuous issues across days
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.config import HISTORY_FILE

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
    """Save history records to history.json (keeps up to 14 days)."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records[-30:], f, ensure_ascii=False, indent=2)

def append_daily_topics(date_str: str, topics: List[Dict[str, Any]]) -> None:
    """Append newly analyzed topics for today's date."""
    history = load_history()
    # Remove existing entry for the same date if re-running
    history = [h for h in history if h.get("date") != date_str]
    history.append({
        "date": date_str,
        "topics": topics,
        "updated_at": datetime.now().isoformat()
    })
    save_history(history)

def get_recent_history_context(days: int = 7) -> str:
    """
    Format recent history into a compact context string for the AI prompt
    to prevent repetitive reporting and encourage continuity.
    """
    history = load_history()
    if not history:
        return "ไม่มีประวัติการรายงานข่าวก่อนหน้า (รายงานเป็นวันแรก)"

    cutoff = datetime.now() - timedelta(days=days)
    recent_entries = []
    
    for entry in history[-days:]:
        d_str = entry.get("date", "")
        topic_list = entry.get("topics", [])
        if not topic_list:
            continue
        items_summary = []
        for t in topic_list:
            title = t.get("title", "") if isinstance(t, dict) else str(t)
            theme = t.get("theme", "") if isinstance(t, dict) else ""
            items_summary.append(f"- {title} ({theme})" if theme else f"- {title}")
        
        recent_entries.append(f"วันที่ {d_str}:\n" + "\n".join(items_summary))
    
    if not recent_entries:
        return "ไม่มีประวัติการรายงานข่าวในช่วง 7 วันที่ผ่านมา"
        
    return "\n\n".join(recent_entries)

if __name__ == "__main__":
    print(get_recent_history_context())
