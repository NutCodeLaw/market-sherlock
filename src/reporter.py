"""
Reporter Module - Generates LATEST.md, archives/YYYY-MM-DD.md, README.md, and pre-rendered web/index.html
"""
import json
import html
from typing import Dict, Any
from pathlib import Path
from src.config import LATEST_MD_PATH, README_MD_PATH, ARCHIVES_DIR, INDEX_HTML_PATH, ROOT_INDEX_HTML_PATH
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

def build_prerendered_html(data: Dict[str, Any], raw_markdown: str) -> str:
    """Build complete, pre-rendered standalone HTML so no client-side JS is needed to display data."""
    date_display = html.escape(data.get("date_formatted", "") or data.get("date", ""))
    time_display = html.escape(data.get("time", ""))
    
    # 1. Snapshot Cards
    snapshot_cards_html = []
    for item in data.get("snapshot_items", []):
        pct = item.get("percent_change", 0.0)
        chg_class = "up" if pct > 0 else ("down" if pct < 0 else "neutral")
        name = html.escape(str(item.get("name", "")))
        sym = html.escape(str(item.get("symbol", "")))
        price = html.escape(str(item.get("price_display", "")))
        chg = html.escape(str(item.get("change_display", "")))
        status = html.escape(str(item.get("status", "⚪")))
        
        card = f"""
            <div class="ticker-card">
                <div class="ticker-name">{name} ({sym})</div>
                <div class="ticker-price">{price}</div>
                <div class="ticker-change {chg_class}">{status} {chg}</div>
            </div>"""
        snapshot_cards_html.append(card)
    snapshot_rendered = "\n".join(snapshot_cards_html)
    
    # 2. Main Stories
    main_stories_html = []
    for story in data.get("main_stories", []):
        title = html.escape(str(story.get("title", "")))
        summary = html.escape(str(story.get("summary", "")))
        takeaway = html.escape(str(story.get("takeaway", "")))
        continuity = html.escape(str(story.get("continuity", "ประเด็นใหม่ล่าสุด")))
        source_name = html.escape(str(story.get("source_name", "Verified Source")))
        source_url = html.escape(str(story.get("source_url", "#")))
        
        card = f"""
        <div class="story-card">
            <h3 class="story-title">{title}</h3>
            <div class="story-body">{summary}</div>
            <div class="takeaway-box">
                <div class="takeaway-title">🎯 Actionable Takeaways</div>
                <div class="takeaway-content">{takeaway}</div>
            </div>
            <div class="story-footer">
                <span>🔄 ความต่อเนื่อง: <strong>{continuity}</strong></span>
                <a class="source-pill" href="{source_url}" target="_blank" rel="noopener noreferrer">🔗 แหล่งข่าว: {source_name}</a>
            </div>
        </div>"""
        main_stories_html.append(card)
    stories_rendered = "\n".join(main_stories_html)
    
    # 3. Market Briefs
    briefs_html = []
    for b in data.get("market_briefs", []):
        tag = html.escape(str(b.get("tag", "#MARKET")))
        headline = html.escape(str(b.get("headline", "")))
        text = html.escape(str(b.get("text", "")))
        item = f"""
        <div class="brief-item">
            <span class="brief-tag">{tag}</span>
            <div class="brief-headline">{headline}</div>
            <div class="brief-text">{text}</div>
        </div>"""
        briefs_html.append(item)
    briefs_rendered = "\n".join(briefs_html)
    
    # 4. Watchlist
    watchlist_items = []
    for w in data.get("watchlist", []):
        t = html.escape(str(w.get("time", "ตลอดวัน")))
        ev = html.escape(str(w.get("event", "")))
        watchlist_items.append(f"<li>⏱️ <strong>{t}:</strong> {ev}</li>")
    watchlist_rendered = f"<ul class='strategy-list'>{''.join(watchlist_items)}</ul>"
    
    # 5. Strategies
    beneficiaries_rendered = "".join([f"<li>{html.escape(str(x))}</li>" for x in data.get("beneficiaries", [])])
    risks_rendered = "".join([f"<li>{html.escape(str(x))}</li>" for x in data.get("risks", [])])
    strategies_rendered = "".join([f"<li>{html.escape(str(x))}</li>" for x in data.get("strategies", [])])
    
    escaped_raw_markdown = html.escape(raw_markdown)

    html_template = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕵️‍♂️ MarketSherlock — สรุปข่าวเศรษฐกิจและพลวัตการลงทุน</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Sarabun:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #090d16;
            --bg-surface: #111827;
            --bg-card: #182234;
            --border: #243248;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-gold: #f59e0b;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --font-display: 'Plus Jakarta Sans', 'Sarabun', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-display);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            padding: 24px 16px;
        }}

        .container {{
            max-width: 1040px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
            gap: 16px;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-icon {{
            font-size: 2.2rem;
            background: linear-gradient(135deg, #1e293b, #0f172a);
            padding: 8px 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}

        .brand-title {{
            font-size: 1.6rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #f8fafc, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .brand-sub {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .header-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .time-badge {{
            background: rgba(6, 182, 212, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-family: var(--font-mono);
            font-weight: 600;
        }}

        .status-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            margin-right: 6px;
            box-shadow: 0 0 10px var(--accent-green);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.25rem;
            font-weight: 700;
            margin: 32px 0 16px 0;
            color: #ffffff;
            border-left: 4px solid var(--accent-gold);
            padding-left: 12px;
        }}

        .snapshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }}

        .ticker-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .ticker-card:hover {{
            transform: translateY(-2px);
            border-color: #3b82f6;
        }}

        .ticker-name {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}

        .ticker-price {{
            font-size: 1.25rem;
            font-weight: 700;
            font-family: var(--font-mono);
            margin-bottom: 4px;
        }}

        .ticker-change {{
            font-size: 0.8rem;
            font-family: var(--font-mono);
            font-weight: 600;
        }}

        .up {{ color: var(--accent-green); }}
        .down {{ color: var(--accent-red); }}
        .neutral {{ color: var(--text-muted); }}

        .story-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            position: relative;
            overflow: hidden;
        }}

        .story-card::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(to bottom, #3b82f6, #06b6d4);
        }}

        .story-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 10px;
            color: #f8fafc;
        }}

        .story-body {{
            font-size: 0.95rem;
            color: #cbd5e1;
            margin-bottom: 14px;
        }}

        .takeaway-box {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 12px;
        }}

        .takeaway-title {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--accent-gold);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}

        .takeaway-content {{
            font-size: 0.9rem;
            color: #e2e8f0;
        }}

        .story-footer {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.82rem;
            gap: 8px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .source-pill {{
            background: rgba(255, 255, 255, 0.06);
            color: #93c5fd;
            text-decoration: none;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: background 0.2s;
        }}

        .source-pill:hover {{
            background: rgba(255, 255, 255, 0.12);
            text-decoration: underline;
        }}

        .briefs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 14px;
        }}

        .brief-item {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
        }}

        .brief-tag {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            font-family: var(--font-mono);
            background: rgba(245, 158, 11, 0.12);
            color: var(--accent-gold);
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 8px;
        }}

        .brief-headline {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 6px;
        }}

        .brief-text {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .strategy-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 14px;
        }}

        .strategy-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
        }}

        .box-heading {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95rem;
            font-weight: 700;
            margin-bottom: 12px;
        }}

        .box-green {{ border-top: 3px solid var(--accent-green); }}
        .box-red {{ border-top: 3px solid var(--accent-red); }}
        .box-blue {{ border-top: 3px solid var(--accent-cyan); }}

        .strategy-list {{
            list-style: none;
            font-size: 0.88rem;
            color: #cbd5e1;
        }}

        .strategy-list li {{
            position: relative;
            padding-left: 18px;
            margin-bottom: 8px;
        }}

        .strategy-list li::before {{
            content: "•";
            position: absolute;
            left: 4px;
            color: var(--accent-gold);
            font-weight: bold;
        }}

        footer {{
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.82rem;
        }}

        .actions-bar {{
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-bottom: 16px;
        }}

        .btn {{
            background: var(--bg-surface);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }}

        .btn:hover {{
            background: var(--bg-card);
            border-color: #64748b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Nav & Brand -->
        <header>
            <div class="brand">
                <div class="brand-icon">🕵️‍♂️</div>
                <div>
                    <h1 class="brand-title">MarketSherlock</h1>
                    <div class="brand-sub">สรุปข่าวเศรษฐกิจและพลวัตการลงทุนรอบโลก (08:00 น.)</div>
                </div>
            </div>
            <div class="header-meta">
                <div class="time-badge">
                    <span class="status-dot"></span>
                    <span id="report-date">{date_display} ({time_display})</span>
                </div>
            </div>
        </header>

        <div class="actions-bar">
            <button class="btn" onclick="window.print()">🖨️ พิมพ์ / บันทึก PDF</button>
            <button class="btn" onclick="copyMarkdown()">📋 คัดลอก Markdown</button>
        </div>

        <!-- 1. Market Snapshot -->
        <div class="section-header">📊 Market Snapshot (ภาพรวมตัวเลขตลาดสำคัญ)</div>
        <div class="snapshot-grid" id="snapshot-container">
{snapshot_rendered}
        </div>

        <!-- 2. Main Stories -->
        <div class="section-header">🔍 ข่าวหลักและการวิเคราะห์เชิงลึก (Investigative & Main Stories)</div>
        <div id="main-stories-container">
{stories_rendered}
        </div>

        <!-- 3. Market Briefs -->
        <div class="section-header">⚡ สรุปข่าวสั้นรอบตลาด (Market Briefs)</div>
        <div class="briefs-grid" id="market-briefs-container">
{briefs_rendered}
        </div>

        <!-- 4. Today's Watchlist -->
        <div class="section-header">📅 วาระเศรษฐกิจต้องจับตาวันนี้ (Today's Watchlist)</div>
        <div class="strategy-box" style="margin-bottom: 24px;" id="watchlist-container">
{watchlist_rendered}
        </div>

        <!-- 5. Deep Insights & Portfolio Compass -->
        <div class="section-header">🧭 ข้อมูลเชิงลึก & กลยุทธ์พอร์ตโฟลิโอ (Strategic Portfolio Compass)</div>
        <div class="strategy-container">
            <div class="strategy-box box-green">
                <div class="box-heading" style="color: var(--accent-green);">🟢 กลุ่มที่ได้ประโยชน์ (Beneficiaries)</div>
                <ul class="strategy-list" id="beneficiaries-list">
{beneficiaries_rendered}
                </ul>
            </div>
            <div class="strategy-box box-red">
                <div class="box-heading" style="color: var(--accent-red);">🔴 กลุ่มที่ต้องระวัง (Risk Watchlist)</div>
                <ul class="strategy-list" id="risks-list">
{risks_rendered}
                </ul>
            </div>
            <div class="strategy-box box-blue">
                <div class="box-heading" style="color: var(--accent-cyan);">💡 นัยเชิงกลยุทธ์ (Strategic Takeaways)</div>
                <ul class="strategy-list" id="strategy-list">
{strategies_rendered}
                </ul>
            </div>
        </div>

        <footer>
            MarketSherlock v1.0 • พัฒนาด้วย Google Gemini 3.8 Flash & Python Autonomous Pipeline • แหล่งข่าว: Bloomberg, Reuters, FT, WSJ, ก.ล.ต., ธปท., ตลาดหลักทรัพย์ฯ, สภาพัฒน์
        </footer>
    </div>

    <!-- Hidden markdown storage for copy button -->
    <textarea id="raw-markdown-data" style="display:none;">{escaped_raw_markdown}</textarea>

    <script>
        function copyMarkdown() {{
            const md = document.getElementById('raw-markdown-data').value;
            navigator.clipboard.writeText(md).then(() => {{
                alert("คัดลอกสรุป Markdown เรียบร้อยแล้ว!");
            }}).catch(() => {{
                alert("ไม่สามารถคัดลอกได้");
            }});
        }}
    </script>
</body>
</html>
"""
    return html_template

def save_all_reports(payload: Dict[str, Any], raw_markdown: str) -> None:
    """Save report to LATEST.md, archives/YYYY-MM-DD.md, README.md, web/index.html, and root index.html."""
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
[![Live Terminal Reader](https://img.shields.io/badge/Web%20Reader-GitHub%20Pages-success)](https://nutcodelaw.github.io/market-sherlock/)

---

## 📖 สรุปข่าวล่าสุด (Latest Morning Dispatch)
👉 **เปิดอ่านรายงานฉบับเต็ม:** [`LATEST.md`](./LATEST.md) หรือเปิด **[🌐 Web Terminal Reader](https://nutcodelaw.github.io/market-sherlock/)**

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
        
    # 4. Generate Pre-rendered HTML
    rendered_html = build_prerendered_html(payload, raw_markdown)
    
    # Save to web/index.html and root index.html
    INDEX_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    with open(ROOT_INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(rendered_html)
