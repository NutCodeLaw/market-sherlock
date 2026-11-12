"""
Reporter Module - Generates LATEST.md, archives/YYYY-MM-DD.md, README.md, and web/index.html
"""
import json
import re
from typing import Dict, Any
from pathlib import Path
from src.config import LATEST_MD_PATH, README_MD_PATH, ARCHIVES_DIR, INDEX_HTML_PATH
from src.utils import get_now_bangkok, format_thai_date, get_iso_date

def generate_markdown_report(data: Dict[str, Any]) -> str:
    """Generate clean, emoji-rich Markdown format according to user specifications."""
    now = get_now_bangkok()
    thai_date = format_thai_date(now)
    time_str = now.strftime("%H:%M น.")
    
    lines = [
        f"# 🕵️‍♂️ สรุปข่าวเศรษฐกิจทั่วโลก (8.00 น.) — {thai_date}",
        f"*อัปเดตอัตโนมัติโดย MarketSherlock • เวลา {time_str} (Asia/Bangkok)*\n",
        "---",
        "",
        "## 📊 Market Snapshot (ภาพรวมตัวเลขตลาดสำคัญ)",
        "",
        data.get("snapshot_markdown", ""),
        "",
        "---",
        "",
        "## 🔍 ข่าวหลักและการวิเคราะห์เชิงลึก (Main Stories)",
        ""
    ]
    
    # Main stories
    for idx, story in enumerate(data.get("main_stories", []), 1):
        lines.append(f"### {idx}. {story.get('title', 'ข่าวเศรษฐกิจสำคัญ')}")
        lines.append(f"{story.get('summary', '')}\n")
        lines.append("> [!TIP]")
        lines.append(f"> **🎯 Actionable Takeaways:** {story.get('takeaway', '')}")
        lines.append(f"> ")
        lines.append(f"> 🔄 **ความต่อเนื่อง:** {story.get('continuity', 'ประเด็นใหม่ล่าสุด')}")
        lines.append(f"> ")
        source_name = story.get('source_name', 'Verified News')
        source_url = story.get('source_url', '#')
        lines.append(f"> 🔗 **แหล่งที่มา:** [{source_name}]({source_url})\n")
    
    lines.append("---")
    lines.append("")
    lines.append("## ⚡ สรุปข่าวสั้นรอบตลาด (Market Briefs)")
    lines.append("")
    
    # Market briefs
    for b in data.get("market_briefs", []):
        tag = b.get("tag", "#MARKET")
        headline = b.get("headline", "")
        text = b.get("text", "")
        lines.append(f"- **`{tag}` {headline}**: {text}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📅 วาระเศรษฐกิจต้องจับตาวันนี้ (Today's Watchlist)")
    lines.append("")
    
    # Watchlist
    for w in data.get("watchlist", []):
        t = w.get("time", "ตลอดวัน")
        ev = w.get("event", "")
        lines.append(f"- ⏱️ **{t}**: {ev}")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🧭 ข้อมูลเชิงลึก & กลยุทธ์พอร์ตโฟลิโอ (Deep Insights)")
    lines.append("")
    
    # Insights
    lines.append("### 🟢 กลุ่มที่ได้ประโยชน์ (Beneficiaries)")
    for item in data.get("beneficiaries", []):
        lines.append(f"- {item}")
    lines.append("")
    
    lines.append("### 🔴 กลุ่มที่ต้องระวัง (Risk Watchlist)")
    for item in data.get("risks", []):
        lines.append(f"- {item}")
    lines.append("")
    
    lines.append("### 💡 นัยเชิงกลยุทธ์ (Strategic Takeaways)")
    for item in data.get("strategies", []):
        lines.append(f"- {item}")
        
    lines.append("")
    lines.append("---")
    lines.append("*จัดทำและตรวจสอบความถูกต้องโดย MarketSherlock Autonomous Intelligence Pipeline*")
    
    return "\n".join(lines)

def save_all_reports(payload: Dict[str, Any], raw_markdown: str) -> None:
    """Save report to LATEST.md, archives/YYYY-MM-DD.md, README.md, and web/index.html."""
    iso_date = payload.get("date", get_iso_date())
    
    # 1. Save LATEST.md
    with open(LATEST_MD_PATH, "w", encoding="utf-8") as f:
        f.write(raw_markdown)
        
    # 2. Save archives/YYYY-MM-DD.md
    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
    archive_file = ARCHIVES_DIR / f"{iso_date}.md"
    with open(archive_file, "w", encoding="utf-8") as f:
        f.write(raw_markdown)
        
    # 3. Update README.md with Header & Embedded Latest Brief
    readme_content = f"""# 🕵️‍♂️ MarketSherlock (มาร์เก็ต เชอร์ล็อก)

> **Autonomous Morning Financial Intelligence & Investigative Briefing Engine**  
> ปฏิบัติการเจาะลึกพลวัตการลงทุนรอบโลกและตลาดไทย ส่งตรงถึงคุณทุกเช้าเวลา 08:00 น.

[![Daily Dispatch](https://github.com/NutCodeLaw/market-sherlock/actions/workflows/daily_dispatch.yml/badge.svg)](https://github.com/NutCodeLaw/market-sherlock/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered By: Gemini 3.8 Flash](https://img.shields.io/badge/AI-Gemini%203.8%20Flash-blue)](https://ai.google.dev/)
[![Live Terminal Reader](https://img.shields.io/badge/Web%20Reader-GitHub%20Pages-success)](./web/index.html)

---

## 📖 สรุปข่าวล่าสุด (Latest Morning Dispatch)
👉 **เปิดอ่านรายงานฉบับเต็ม:** [`LATEST.md`](./LATEST.md) หรือเปิด **[Web Terminal Reader](./web/index.html)**

{raw_markdown}

---

## 🏛️ สถาปัตยกรรมระบบ (Architecture)
1. **Market Fetcher (`src/market_fetcher.py`)**: ดึงดัชนี SET, S&P 500, US 10Y Yield, Crude Oil, Gold, USD/THB ด้วย `yfinance` แบบ 100% Real-time
2. **AI Investigator (`src/ai_investigator.py`)**: ขับเคลื่อนด้วย Google Gemini 3.8 Flash พร้อม Google Search Grounding สแกนข่าวเด่น 24 ชม. และเจาะลึกนัยเชิงโครงสร้าง
3. **State Tracker (`src/state_manager.py`)**: จดจำประเด็นข่าวย้อนหลัง 7 วัน ป้องกันการรายงานข่าวซ้ำ และตามติดความคืบหน้าของเรื่องราวอย่างต่อเนื่อง
4. **Multi-Format Publisher (`src/reporter.py`)**: จัดพิมพ์รายงานลง `LATEST.md`, เก็บเข้า `archives/`, และอัปเดตหน้า Dashboard Web Reader ทันที
5. **Autonomous Cron (`.github/workflows/daily_dispatch.yml`)**: ทำงานบน GitHub Actions Serverless ฟรี 100% ปลุกตัวเองมารันทุกเช้า 07:50 น. เพื่อให้พร้อมอ่านตอน 08:00 น.

## 💻 การติดตั้งและรันในเครื่อง (Local Setup)
```bash
# 1. Clone repository
git clone https://github.com/NutCodeLaw/market-sherlock.git
cd market-sherlock

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup API Key in .env
cp .env.example .env
# ใส่ GEMINI_API_KEY ของคุณในไฟล์ .env

# 4. Run investigator
python main.py
```
"""
    with open(README_MD_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    # 4. Inject payload into web/index.html
    if INDEX_HTML_PATH.exists():
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        
        # Inject JSON
        json_str = json.dumps(payload, ensure_ascii=False, indent=2)
        html = re.sub(r'<script id="briefing-data" type="application/json">[\s\S]*?</script>',
                      f'<script id="briefing-data" type="application/json">\n{json_str}\n    </script>',
                      html)
        
        # Inject Raw Markdown for copy button
        escaped_md = json.dumps(raw_markdown, ensure_ascii=False)
        html = re.sub(r'window\.__RAW_MARKDOWN__\s*=[\s\S]*?;',
                      f'window.__RAW_MARKDOWN__ = {escaped_md};',
                      html)
        if 'window.__RAW_MARKDOWN__' not in html:
            html = html.replace('window.addEventListener(\'DOMContentLoaded\', renderBriefing);',
                                f'window.__RAW_MARKDOWN__ = {escaped_md};\n        window.addEventListener(\'DOMContentLoaded\', renderBriefing);')
                                
        with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(html)
