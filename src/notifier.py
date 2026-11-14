"""
Telegram Notifier Module - Weekly Executive Fast-Bite (Guaranteed Safe Length & CI Guard)
"""
import os
import sys
import json
import html
import urllib.request
import urllib.parse
from typing import Dict, Any

# Telegram API hard limit is 4,096 chars; we enforce a strict conservative limit of 3,500 chars
TELEGRAM_MAX_CHARS = 3500

def truncate_text(text: str, max_len: int) -> str:
    """Trim string to max_len safely with ellipsis."""
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."

def send_telegram_briefing(payload: Dict[str, Any]) -> bool:
    """
    Send an ultra-compact, punchy weekly summary to Telegram every Monday at 08:00 AM BKK.
    Guarded so local runs do not accidentally broadcast unless --telegram or FORCE_TELEGRAM is set.
    """
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    force_tg = os.environ.get("FORCE_TELEGRAM", "").lower() in ["true", "1", "yes"] or "--telegram" in sys.argv
    if not is_ci and not force_tg:
        print("[Notifier] Local environment detected. Telegram dispatch paused (will auto-send in GitHub Actions every Monday 08:00 AM BKK).")
        return False

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    
    if not bot_token or not chat_id:
        print("[Notifier] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not provided. Skipping Telegram notification.")
        return False
        
    date_str = html.escape(payload.get("date_formatted", payload.get("date", "วันนี้")))
    time_str = html.escape(payload.get("time", "08:00 น."))
    
    # 1. Format Snapshot (Pairing 2 items per line for ultra-compact vertical space)
    items = payload.get("snapshot_items", [])
    snapshot_lines = []
    
    # Custom compact mapper
    for it in items:
        name = it.get("name", it.get("symbol", ""))
        price = it.get("price_display", "")
        status = it.get("status", "")
        pct = it.get("percent_change", 0.0)
        sign = "+" if pct > 0 else ""
        compact_chg = f"{sign}{pct:.2f}%" if pct != 0 else "0.00%"
        
        # Shorten names for cleaner mobile display
        short_name = (
            "SET" if "SET" in name else
            ("S&P500" if "S&P" in name else
            ("US 10Y" if "10Y" in name else
            ("WTI Oil" if "Oil" in name else
            ("Gold" if "Gold" in name else
            ("USD/THB" if "THB" in name else name)))))
        )
        snapshot_lines.append(f"• <b>{short_name}:</b> <code>{price}</code> ({status} {compact_chg})")
        
    snapshot_text = "\n".join(snapshot_lines)
    
    # 2. Format Top 3 Headlines (Concise & punchy, no long summaries)
    story_lines = []
    emojis = ["1️⃣", "2️⃣", "3️⃣"]
    for idx, story in enumerate(payload.get("main_stories", [])[:3]):
        icon = emojis[idx] if idx < len(emojis) else f"{idx+1}."
        title = html.escape(truncate_text(story.get("title", ""), 110))
        takeaway = html.escape(truncate_text(story.get("takeaway", ""), 95))
        
        story_lines.append(f"{icon} <b>{title}</b>\n   ↳ <i>{takeaway}</i>")
        
    stories_text = "\n\n".join(story_lines)
    
    # 3. Compact Strategy Compass
    raw_b = payload.get("beneficiaries", [])
    raw_r = payload.get("risks", [])
    raw_s = payload.get("strategies", [])
    
    beneficiaries = html.escape(truncate_text(", ".join(raw_b[:2]), 85)) if raw_b else "-"
    risks = html.escape(truncate_text(", ".join(raw_r[:2]), 85)) if raw_r else "-"
    strategy = html.escape(truncate_text(raw_s[0], 110)) if raw_s else "เน้นบริหารความเสี่ยงเชิงรุก"

    # Assemble compact weekly message
    week_id = html.escape(payload.get("week_id", ""))
    week_tag = f" • {week_id}" if week_id else ""
    message = (
        f"🕵️‍♂️ <b>MarketSherlock Weekly Strategy (จันทร์ 08:00 น.)</b>\n"
        f"📅 <i>{date_str}{week_tag} • {time_str}</i>\n\n"
        f"📊 <b>1W Market Snapshot:</b>\n"
        f"{snapshot_text}\n\n"
        f"🔍 <b>3 มหาประเด็นชี้ขาดรอบสัปดาห์:</b>\n"
        f"{stories_text}\n\n"
        f"🧭 <b>กลยุทธ์พอร์ตโฟลิโอประจำสัปดาห์:</b>\n"
        f"🟢 <b>บวก:</b> {beneficiaries}\n"
        f"🔴 <b>ระวัง:</b> {risks}\n"
        f"💡 <b>กลยุทธ์:</b> {strategy}\n\n"
        f"👉 <b>เปิดอ่านรายงานฉบับเต็ม + Weekly Cockpit:</b>\n"
        f"🔗 <a href='https://nutcodelaw.github.io/market-sherlock/'>https://nutcodelaw.github.io/market-sherlock/</a>"
    )
    
    # Enforce safe character limit guard cleanly at line boundary to avoid breaking HTML tags
    if len(message) > TELEGRAM_MAX_CHARS:
        footer = "\n\n👉 <a href='https://nutcodelaw.github.io/market-sherlock/'>เปิดอ่านฉบับเต็มบนเว็บ</a>"
        cutoff = message.rfind("\n", 0, TELEGRAM_MAX_CHARS - len(footer) - 20)
        message = (message[:cutoff] if cutoff > 0 else message[:TELEGRAM_MAX_CHARS - len(footer) - 20]) + footer
        
    print(f"[Notifier] Message length: {len(message)} / 4096 characters (Safe & Compact)")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    post_data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(post_data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("ok"):
                print("[Notifier] 🚀 สรุปข่าวแบบ Compact ถูกส่งเข้า Telegram เรียบร้อยแล้ว!")
                return True
            else:
                print(f"[Notifier] ❌ Telegram API error: {res_json}")
                return False
    except Exception as e:
        print(f"[Notifier] ❌ ส่งเข้า Telegram ไม่สำเร็จ: {e}")
        return False
