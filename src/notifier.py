"""
Telegram Notifier Module - Sends executive morning briefs to Telegram channel or direct chat
"""
import os
import json
import urllib.request
import urllib.parse
from typing import Dict, Any

def send_telegram_briefing(payload: Dict[str, Any]) -> bool:
    """Send formatted morning financial briefing to Telegram."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    
    if not bot_token or not chat_id:
        print("[Notifier] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not provided. Skipping Telegram notification.")
        return False
        
    date_str = payload.get("date_formatted", payload.get("date", "วันนี้"))
    time_str = payload.get("time", "08:00 น.")
    
    # 1. Format Snapshot
    snapshot_lines = []
    for item in payload.get("snapshot_items", []):
        sym = item.get("name", item.get("symbol", ""))
        price = item.get("price_display", "")
        chg = item.get("change_display", "")
        status = item.get("status", "")
        snapshot_lines.append(f"• <b>{sym}</b>: <code>{price}</code> ({status} {chg})")
    snapshot_text = "\n".join(snapshot_lines)
    
    # 2. Format Top Stories
    story_lines = []
    for idx, story in enumerate(payload.get("main_stories", [])[:3], 1):
        title = story.get("title", "")
        takeaway = story.get("takeaway", "")
        source = story.get("source_name", "ข่าวกรอง")
        url = story.get("source_url", "https://nutcodelaw.github.io/market-sherlock/")
        story_lines.append(
            f"<b>{idx}. {title}</b>\n"
            f"🎯 <i>Takeaway: {takeaway}</i>\n"
            f"🔗 <a href='{url}'>{source}</a>"
        )
    stories_text = "\n\n".join(story_lines)
    
    # 3. Strategy Compass
    beneficiaries = ", ".join(payload.get("beneficiaries", [])[:2])
    risks = ", ".join(payload.get("risks", [])[:2])
    strategy = payload.get("strategies", ["เน้นถือเงินสดและหุ้นปันผล"])[0] if payload.get("strategies") else "บริหารความเสี่ยงเชิงรุก"

    message = (
        f"🕵️‍♂️ <b>MarketSherlock (8.00 น.)</b>\n"
        f"📅 ประจำวันที่ {date_str} • {time_str}\n\n"
        f"📊 <b>Market Snapshot:</b>\n"
        f"{snapshot_text}\n\n"
        f"🔍 <b>3 ข่าวหลักเจาะลึก:</b>\n"
        f"{stories_text}\n\n"
        f"🧭 <b>กลยุทธ์พอร์ตโฟลิโอ:</b>\n"
        f"🟢 <b>ได้ประโยชน์:</b> {beneficiaries}\n"
        f"🔴 <b>ต้องระวัง:</b> {risks}\n"
        f"💡 <b>กลยุทธ์:</b> {strategy}\n\n"
        f"🌐 <b>อ่านรายงานฉบับเต็มพร้อมกราฟ:</b>\n"
        f"👉 <a href='https://nutcodelaw.github.io/market-sherlock/'>https://nutcodelaw.github.io/market-sherlock/</a>"
    )
    
    # Send via Telegram API
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
                print("[Notifier] 🚀 สรุปข่าวถูกส่งเข้า Telegram เรียบร้อยแล้ว!")
                return True
            else:
                print(f"[Notifier] ❌ Telegram API returned error: {res_json}")
                return False
    except Exception as e:
        print(f"[Notifier] ❌ ไม่สามารถส่งข้อความเข้า Telegram ได้: {e}")
        return False
