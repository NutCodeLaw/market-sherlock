"""
Reporter Module - Generates LATEST.md, archives/YYYY-MM-DD.md, README.md, and Interactive Financial Cockpit
"""
import json
import html
from typing import Dict, Any, List
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
        f"*อัปเดตอัตโนมัติโดย MarketSherlock Financial Cockpit • เวลา {time_str} (Asia/Bangkok)*\n",
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
    
    for idx, story in enumerate(data.get("main_stories", []), 1):
        threat = "⭐" * int(story.get("threat_level", 4))
        lines.append(f"### {idx}. {story.get('title', 'ข่าวสำคัญ')} {threat}")
        lines.append(f"> **⚡ TL;DR:** {story.get('tldr', story.get('summary', ''))}\n")
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
    
    for w in data.get("watchlist", []):
        t = w.get("time", "ตลอดวัน")
        ev = w.get("event", "")
        lines.append(f"- ⏱️ **{t}**: {ev}")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🧭 ข้อมูลเชิงลึก & กลยุทธ์พอร์ตโฟลิโอ (Deep Insights)")
    lines.append("")
    
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
    """Build the high-octane 5-module Financial Cockpit HTML."""
    date_display = html.escape(data.get("date_formatted", "") or data.get("date", ""))
    time_display = html.escape(data.get("time", ""))
    
    # 1. Market Sentiment Score (0 to 100)
    sentiment = data.get("market_sentiment", {})
    sent_score = int(sentiment.get("score", 50))
    sent_label = html.escape(sentiment.get("label", "Neutral"))
    sent_rationale = html.escape(sentiment.get("rationale", "ตลาดอยู่ในช่วงจับตาทิศทางดอกเบี้ยโลกและกระแสเงินทุน"))
    
    # Needle degree for SVG speedometer (from -90deg to +90deg)
    # score 0 = -90deg, 50 = 0deg, 100 = 90deg
    needle_deg = ((sent_score / 100.0) * 180.0) - 90.0
    
    # Sentiment status color
    if sent_score >= 60:
        sent_color = "#10b981" # Green
    elif sent_score <= 40:
        sent_color = "#ef4444" # Red
    else:
        sent_color = "#f59e0b" # Yellow
        
    # 2. Asset Heatmap Grid (Finviz style)
    heatmap_cards_html = []
    for item in data.get("snapshot_items", []):
        pct = item.get("percent_change", 0.0)
        # Background intensity based on percent change
        if pct > 0.5:
            box_bg = "rgba(16, 185, 129, 0.25)"
            border_c = "#10b981"
            txt_c = "#34d399"
        elif pct > 0.05:
            box_bg = "rgba(16, 185, 129, 0.12)"
            border_c = "#059669"
            txt_c = "#10b981"
        elif pct < -0.5:
            box_bg = "rgba(239, 68, 68, 0.25)"
            border_c = "#ef4444"
            txt_c = "#f87171"
        elif pct < -0.05:
            box_bg = "rgba(239, 68, 68, 0.12)"
            border_c = "#dc2626"
            txt_c = "#ef4444"
        else:
            box_bg = "rgba(100, 116, 139, 0.12)"
            border_c = "#475569"
            txt_c = "#94a3b8"

        name = html.escape(str(item.get("name", "")))
        sym = html.escape(str(item.get("symbol", "")))
        price = html.escape(str(item.get("price_display", "")))
        chg = html.escape(str(item.get("change_display", "")))
        status = html.escape(str(item.get("status", "⚪")))
        
        card = f"""
        <div class="heatmap-tile" style="background: {box_bg}; border-color: {border_c};">
            <div class="heatmap-header">
                <span class="heatmap-name">{name}</span>
                <span class="heatmap-sym">{sym}</span>
            </div>
            <div class="heatmap-price">{price}</div>
            <div class="heatmap-chg" style="color: {txt_c};">{status} {chg}</div>
        </div>"""
        heatmap_cards_html.append(card)
    heatmap_rendered = "\n".join(heatmap_cards_html)
    
    # 3. Bento Grid Crime Files (with TL;DR toggle)
    bento_cards_html = []
    for idx, story in enumerate(data.get("main_stories", []), 1):
        threat_stars = "⭐" * int(story.get("threat_level", 4))
        title = html.escape(str(story.get("title", "")))
        tldr = html.escape(str(story.get("tldr", story.get("summary", ""))))
        summary = html.escape(str(story.get("summary", "")))
        takeaway = html.escape(str(story.get("takeaway", "")))
        continuity = html.escape(str(story.get("continuity", "ประเด็นใหม่ล่าสุด")))
        source_name = html.escape(str(story.get("source_name", "Verified Source")))
        source_url = html.escape(str(story.get("source_url", "#")))
        card_id = f"crime-file-{idx}"
        
        card = f"""
        <div class="bento-card">
            <div class="bento-badge-row">
                <span class="bento-tag">📂 แฟ้มคดีที่ {idx}</span>
                <span class="bento-threat">ความเร่งด่วน: {threat_stars}</span>
            </div>
            <h3 class="bento-title">{title}</h3>
            
            <!-- Quick TL;DR Box -->
            <div class="tldr-pill">
                <span class="tldr-label">⚡ TL;DR:</span> {tldr}
            </div>

            <!-- Expandable Detailed Investigation -->
            <div class="bento-deep-dive" id="{card_id}">
                <p class="bento-summary">{summary}</p>
                <div class="takeaway-box">
                    <div class="takeaway-title">🎯 Actionable Takeaways</div>
                    <div class="takeaway-content">{takeaway}</div>
                </div>
                <div class="bento-meta">
                    <span>🔄 ความต่อเนื่อง: <strong>{continuity}</strong></span>
                    <a class="source-pill" href="{source_url}" target="_blank" rel="noopener noreferrer">🔗 แหล่งข่าว: {source_name}</a>
                </div>
            </div>

            <button class="toggle-btn" onclick="toggleDetails('{card_id}', this)">
                <span>🔎 เจาะลึกแฟ้มคดี</span> <span class="arrow-icon">▼</span>
            </button>
        </div>"""
        bento_cards_html.append(card)
    bento_rendered = "\n".join(bento_cards_html)
    
    # 4. Bull vs Bear Tug-of-War
    bb = data.get("bull_bear", {})
    bull_pct = int(bb.get("bull_pct", 50))
    bear_pct = 100 - bull_pct
    bb_summary = html.escape(bb.get("summary", "ตลาดอยู่ในภาวะสมดุลระหว่างแรงซื้อกลุ่มธนาคารและแรงขายหุ้นเทค"))
    
    bull_drivers = "".join([f"<li>🟢 {html.escape(str(x))}</li>" for x in bb.get("bull_drivers", [])])
    bear_drivers = "".join([f"<li>🔴 {html.escape(str(x))}</li>" for x in bb.get("bear_drivers", [])])
    
    # 5. Sherlock's Asset Compass
    allocations = data.get("asset_allocation", [
        {"asset": "เงินสด & ตราสารหนี้สั้น", "pct": 40, "color": "#06b6d4"},
        {"asset": "หุ้นไทยคุณค่า & ปันผลสูง", "pct": 25, "color": "#10b981"},
        {"asset": "หุ้นโลก / เติบโต", "pct": 25, "color": "#3b82f6"},
        {"asset": "ทองคำ & สินทรัพย์ทางเลือก", "pct": 10, "color": "#f59e0b"}
    ])
    
    bar_segments_html = []
    legend_html = []
    for a in allocations:
        pct = a.get("pct", 25)
        color = a.get("color", "#3b82f6")
        name = html.escape(str(a.get("asset", "")))
        bar_segments_html.append(f'<div class="alloc-bar-segment" style="width: {pct}%; background: {color};" title="{name}: {pct}%"></div>')
        legend_html.append(f'<div class="alloc-legend-item"><span class="alloc-dot" style="background: {color};"></span><span>{name} <strong>{pct}%</strong></span></div>')
        
    alloc_bar_rendered = "".join(bar_segments_html)
    alloc_legend_rendered = "".join(legend_html)
    
    # Market Briefs
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
    
    # Watchlist
    watchlist_items = []
    for w in data.get("watchlist", []):
        t = html.escape(str(w.get("time", "ตลอดวัน")))
        ev = html.escape(str(w.get("event", "")))
        watchlist_items.append(f"<li>⏱️ <strong>{t}:</strong> {ev}</li>")
    watchlist_rendered = f"<ul class='strategy-list'>{''.join(watchlist_items)}</ul>"

    # Text for Audio Player (Voice narration)
    speech_text = f"รายงานสรุปข่าวเศรษฐกิจรอบโลก มาร์เก็ตเชอร์ล็อก ประจำวันที่ {date_display} อารมณ์ตลาดวันนี้อยู่ในเกณฑ์ {sent_label} คะแนน {sent_score} เต็ม 100 ดัชนีหลัก "
    for idx, story in enumerate(data.get("main_stories", [])[:3], 1):
        speech_text += f"ข่าวที่ {idx}: {story.get('title', '')} จุดสำคัญคือ {story.get('tldr', '')}. "
    escaped_speech_text = html.escape(speech_text.replace('"', '\\"'))

    escaped_raw_markdown = html.escape(raw_markdown)

    html_template = f"""<!DOCTYPE html>
<html lang="th" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕵️‍♂️ MarketSherlock — Interactive Financial Cockpit</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Sarabun:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
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

        [data-theme="bloomberg"] {{
            --bg-base: #0a0a0a;
            --bg-surface: #141414;
            --bg-card: #1c1c1c;
            --border: #ff9900;
            --text-main: #ff9900;
            --text-muted: #d4a359;
            --accent-gold: #ffaa00;
            --accent-cyan: #00ddff;
        }}

        [data-theme="slate"] {{
            --bg-base: #0f172a;
            --bg-surface: #1e293b;
            --bg-card: #334155;
            --border: #475569;
            --text-main: #f8fafc;
            --text-muted: #cbd5e1;
            --accent-gold: #fbbf24;
            --accent-cyan: #38bdf8;
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
            transition: background-color 0.3s, color 0.3s;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}

        /* Header Cockpit */
        header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 20px;
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
            gap: 10px;
            flex-wrap: wrap;
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

        /* Audio & Controls Bar */
        .controls-bar {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 10px 16px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            gap: 12px;
        }}

        .audio-player-box {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .audio-btn {{
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            color: #ffffff;
            border: none;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: opacity 0.2s;
        }}

        .audio-btn:hover {{ opacity: 0.9; }}

        .audio-status {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .theme-buttons {{
            display: flex;
            gap: 6px;
        }}

        .btn {{
            background: var(--bg-card);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }}

        .btn:hover {{ background: rgba(255, 255, 255, 0.1); }}

        /* Module 1: Split Cockpit (Sentiment Gauge + Finviz Heatmap) */
        .cockpit-top-grid {{
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }}

        @media (max-width: 860px) {{
            .cockpit-top-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .sentiment-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}

        .gauge-svg {{
            width: 220px;
            height: 120px;
            overflow: visible;
        }}

        .gauge-needle {{
            transform-origin: 100px 95px;
            transition: transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}

        .sentiment-val {{
            font-size: 2rem;
            font-weight: 800;
            font-family: var(--font-mono);
            margin-top: 4px;
        }}

        .sentiment-tag {{
            display: inline-block;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 2px 10px;
            border-radius: 9999px;
            margin-bottom: 6px;
        }}

        .sentiment-desc {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.4;
        }}

        /* Finviz Heatmap Tiles */
        .heatmap-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 10px;
        }}

        .heatmap-tile {{
            border: 1px solid;
            border-radius: 12px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}

        .heatmap-tile:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        }}

        .heatmap-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 6px;
        }}

        .heatmap-name {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .heatmap-sym {{
            font-size: 0.72rem;
            font-family: var(--font-mono);
            color: var(--text-muted);
        }}

        .heatmap-price {{
            font-size: 1.25rem;
            font-weight: 800;
            font-family: var(--font-mono);
            margin-bottom: 4px;
        }}

        .heatmap-chg {{
            font-size: 0.82rem;
            font-weight: 700;
            font-family: var(--font-mono);
        }}

        /* Module 2: Bento Grid Crime Files */
        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2rem;
            font-weight: 800;
            margin: 28px 0 16px 0;
            color: #ffffff;
            border-left: 4px solid var(--accent-gold);
            padding-left: 12px;
        }}

        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .bento-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
            transition: border-color 0.2s;
        }}

        .bento-card:hover {{
            border-color: #3b82f6;
        }}

        .bento-badge-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .bento-tag {{
            font-size: 0.75rem;
            font-weight: 700;
            font-family: var(--font-mono);
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .bento-threat {{
            font-size: 0.75rem;
            color: var(--accent-gold);
            font-weight: 600;
        }}

        .bento-title {{
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 12px;
            color: #f8fafc;
            line-height: 1.4;
        }}

        .tldr-pill {{
            background: rgba(15, 23, 42, 0.8);
            border-left: 3px solid var(--accent-cyan);
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 0.88rem;
            color: #e2e8f0;
            margin-bottom: 14px;
            line-height: 1.45;
        }}

        .tldr-label {{
            font-weight: 800;
            color: var(--accent-cyan);
            font-size: 0.78rem;
            text-transform: uppercase;
        }}

        .bento-deep-dive {{
            display: none;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 12px;
        }}

        .bento-deep-dive.open {{
            display: block;
        }}

        .bento-summary {{
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 12px;
            line-height: 1.5;
        }}

        .takeaway-box {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 12px;
        }}

        .takeaway-title {{
            font-size: 0.78rem;
            font-weight: 800;
            color: var(--accent-gold);
            margin-bottom: 4px;
        }}

        .takeaway-content {{
            font-size: 0.86rem;
            color: #f1f5f9;
        }}

        .bento-meta {{
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}

        .source-pill {{
            background: rgba(255, 255, 255, 0.06);
            color: #93c5fd;
            text-decoration: none;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
        }}

        .source-pill:hover {{ text-decoration: underline; }}

        .toggle-btn {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            transition: background 0.2s;
        }}

        .toggle-btn:hover {{ background: rgba(255, 255, 255, 0.1); }}

        /* Module 3: Bull vs Bear Tug-of-War */
        .tug-war-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 24px;
        }}

        .tug-war-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .bull-pct-text {{ color: var(--accent-green); font-family: var(--font-mono); font-size: 1.1rem; }}
        .bear-pct-text {{ color: var(--accent-red); font-family: var(--font-mono); font-size: 1.1rem; }}

        .tug-war-bar {{
            height: 14px;
            border-radius: 9999px;
            display: flex;
            overflow: hidden;
            margin-bottom: 14px;
            background: #1e293b;
        }}

        .tug-bull-fill {{ background: linear-gradient(90deg, #10b981, #34d399); transition: width 1s; }}
        .tug-bear-fill {{ background: linear-gradient(90deg, #f87171, #ef4444); transition: width 1s; }}

        .tug-war-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}

        .army-card {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 12px;
            font-size: 0.85rem;
        }}

        .army-title {{
            font-weight: 800;
            margin-bottom: 6px;
        }}

        .army-list {{
            list-style: none;
            color: #cbd5e1;
            line-height: 1.5;
        }}

        /* Module 4: Asset Allocation Bar */
        .alloc-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 24px;
        }}

        .alloc-bar {{
            height: 20px;
            border-radius: 9999px;
            display: flex;
            overflow: hidden;
            margin: 12px 0 14px 0;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        }}

        .alloc-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            font-size: 0.85rem;
        }}

        .alloc-legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .alloc-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}

        /* Briefs & Watchlist */
        .bottom-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }}

        @media (max-width: 768px) {{
            .bottom-grid, .tug-war-grid {{ grid-template-columns: 1fr; }}
        }}

        .brief-item {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
        }}

        .brief-tag {{
            font-size: 0.7rem;
            font-weight: 700;
            font-family: var(--font-mono);
            background: rgba(245, 158, 11, 0.12);
            color: var(--accent-gold);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .brief-headline {{
            font-size: 0.9rem;
            font-weight: 700;
            color: #f1f5f9;
            margin: 4px 0;
        }}

        .brief-text {{
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        .strategy-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
        }}

        .strategy-list {{
            list-style: none;
            font-size: 0.86rem;
            color: #cbd5e1;
        }}

        .strategy-list li {{
            margin-bottom: 8px;
            line-height: 1.45;
        }}

        footer {{
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.82rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <div class="brand">
                <div class="brand-icon">🕵️‍♂️</div>
                <div>
                    <h1 class="brand-title">MarketSherlock Cockpit</h1>
                    <div class="brand-sub">สรุปข่าวสืบสวนและพลวัตการลงทุนรอบโลก (08:00 น.)</div>
                </div>
            </div>
            <div class="header-meta">
                <div class="time-badge">
                    <span class="status-dot"></span>
                    <span>{date_display} ({time_display})</span>
                </div>
            </div>
        </header>

        <!-- Controls & Audio Narration Bar -->
        <div class="controls-bar">
            <div class="audio-player-box">
                <button class="audio-btn" id="play-voice-btn" onclick="playVoiceSummary()">
                    <span>🔊 ฟังเสียงสรุป 60 วินาที</span>
                </button>
                <span class="audio-status" id="audio-status-text">พร้อมบรรยาย</span>
            </div>
            <div class="theme-buttons">
                <button class="btn" onclick="setTheme('dark')">🌙 Dark</button>
                <button class="btn" onclick="setTheme('bloomberg')">🟡 Terminal</button>
                <button class="btn" onclick="setTheme('slate')">☕ Slate</button>
                <button class="btn" onclick="copyMarkdown()">📋 Copy MD</button>
            </div>
        </div>

        <!-- 1. Market Sentiment Gauge + Finviz Heatmap Grid -->
        <div class="cockpit-top-grid">
            <!-- Sentiment Gauge -->
            <div class="sentiment-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 4px;">🧭 MARKET SENTIMENT</div>
                <svg class="gauge-svg" viewBox="0 0 200 110">
                    <!-- Gauge Arc -->
                    <path d="M 20 95 A 80 80 0 0 1 180 95" fill="none" stroke="#243248" stroke-width="16" stroke-linecap="round"/>
                    <!-- Color Sections -->
                    <path d="M 20 95 A 80 80 0 0 1 65 38" fill="none" stroke="#ef4444" stroke-width="16" stroke-linecap="round"/>
                    <path d="M 68 35 A 80 80 0 0 1 132 35" fill="none" stroke="#f59e0b" stroke-width="16"/>
                    <path d="M 135 38 A 80 80 0 0 1 180 95" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round"/>
                    <!-- Needle -->
                    <g class="gauge-needle" style="transform: rotate({needle_deg}deg);">
                        <polygon points="98,95 102,95 100,24" fill="#ffffff"/>
                        <circle cx="100" cy="95" r="7" fill="{sent_color}"/>
                    </g>
                </svg>
                <div class="sentiment-val" style="color: {sent_color};">{sent_score}</div>
                <div class="sentiment-tag" style="background: rgba(255,255,255,0.1); color: {sent_color};">{sent_label}</div>
                <div class="sentiment-desc">{sent_rationale}</div>
            </div>

            <!-- Heatmap Tiles -->
            <div class="heatmap-grid">
{heatmap_rendered}
            </div>
        </div>

        <!-- 2. Bento Grid Crime Files (3 Main Stories) -->
        <div class="section-header">📂 3 แฟ้มคดีสืบสวนเด่น (Investigative Crime Files)</div>
        <div class="bento-grid">
{bento_rendered}
        </div>

        <!-- 3. Bull vs Bear Tug-of-War -->
        <div class="section-header">🐂⚔️🐻 Bull vs Bear Tug-of-War (สมรภูมิกระทิงปะทะหมี)</div>
        <div class="tug-war-box">
            <div class="tug-war-header">
                <span class="bull-pct-text">🐂 ฝั่งกระทิง (Bulls) {bull_pct}%</span>
                <span style="font-size: 0.8rem; color: var(--text-muted);">{bb_summary}</span>
                <span class="bear-pct-text">🐻 ฝั่งหมี (Bears) {bear_pct}%</span>
            </div>
            <div class="tug-war-bar">
                <div class="tug-bull-fill" style="width: {bull_pct}%;"></div>
                <div class="tug-bear-fill" style="width: {bear_pct}%;"></div>
            </div>
            <div class="tug-war-grid">
                <div class="army-card" style="border-left: 3px solid var(--accent-green);">
                    <div class="army-title" style="color: var(--accent-green);">กองทัพหนุน (Bullish Drivers)</div>
                    <ul class="army-list">{bull_drivers}</ul>
                </div>
                <div class="army-card" style="border-left: 3px solid var(--accent-red);">
                    <div class="army-title" style="color: var(--accent-red);">กองทัพกดดัน (Bearish Risks)</div>
                    <ul class="army-list">{bear_drivers}</ul>
                </div>
            </div>
        </div>

        <!-- 4. Sherlock's Asset Compass -->
        <div class="section-header">🍰 Sherlock’s Daily Asset Compass (สูตรจัดสัดส่วนพอร์ตวันนี้)</div>
        <div class="alloc-card">
            <div style="font-size: 0.85rem; color: var(--text-muted);">คำแนะนำการกระจายสินทรัพย์เพื่อรับมือพลวัตตลาดปัจจุบัน (Total 100%)</div>
            <div class="alloc-bar">
{alloc_bar_rendered}
            </div>
            <div class="alloc-legend">
{alloc_legend_rendered}
            </div>
        </div>

        <!-- 5. Briefs & Watchlist -->
        <div class="bottom-grid">
            <div>
                <div class="section-header" style="margin-top: 0;">⚡ Market Briefs รอบตลาด</div>
{briefs_rendered}
            </div>
            <div>
                <div class="section-header" style="margin-top: 0;">📅 Today's Watchlist & กลยุทธ์</div>
                <div class="strategy-box">
                    <div style="font-weight: 800; color: var(--accent-cyan); margin-bottom: 8px;">วาระสำคัญวันนี้:</div>
{watchlist_rendered}
                    <div style="border-top: 1px solid var(--border); margin: 12px 0;"></div>
                    <div style="font-weight: 800; color: var(--accent-gold); margin-bottom: 6px;">💡 คำแนะนำกลยุทธ์หลัก:</div>
                    <div style="font-size: 0.88rem; color: #f1f5f9;">{html.escape(data.get('strategies', ['เน้น Selective Value'])[0] if data.get('strategies') else '')}</div>
                </div>
            </div>
        </div>

        <footer>
            MarketSherlock Cockpit v2.0 • ขับเคลื่อนด้วย Google Gemini 3.8 Flash VIP & Python Autonomous Pipeline • แหล่งข่าว: Bloomberg, Reuters, FT, WSJ, ก.ล.ต., ธปท., ตลาดหลักทรัพย์ฯ, สภาพัฒน์
        </footer>
    </div>

    <!-- Hidden Raw Markdown for Copy Button -->
    <textarea id="raw-markdown-data" style="display:none;">{escaped_raw_markdown}</textarea>

    <!-- Client-side Interactive Logic -->
    <script>
        function toggleDetails(id, btn) {{
            const el = document.getElementById(id);
            if (el.classList.contains('open')) {{
                el.classList.remove('open');
                btn.querySelector('span').textContent = '🔎 เจาะลึกแฟ้มคดี';
                btn.querySelector('.arrow-icon').textContent = '▼';
            }} else {{
                el.classList.add('open');
                btn.querySelector('span').textContent = '📁 ย่อเก็บแฟ้ม';
                btn.querySelector('.arrow-icon').textContent = '▲';
            }}
        }}

        function setTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('ms_theme', theme);
        }}

        const savedTheme = localStorage.getItem('ms_theme');
        if (savedTheme) {{
            setTheme(savedTheme);
        }}

        function copyMarkdown() {{
            const md = document.getElementById('raw-markdown-data').value;
            navigator.clipboard.writeText(md).then(() => {{
                alert("📋 คัดลอกรายงานสรุป Markdown เรียบร้อยแล้ว!");
            }});
        }}

        // Native Browser Voice Narration
        let isSpeaking = false;
        const voiceText = "{escaped_speech_text}";

        function playVoiceSummary() {{
            if (!('speechSynthesis' in window)) {{
                alert("เบราว์เซอร์ของคุณไม่รองรับการอ่านออกเสียง");
                return;
            }}

            const btn = document.getElementById('play-voice-btn');
            const status = document.getElementById('audio-status-text');

            if (isSpeaking) {{
                window.speechSynthesis.cancel();
                isSpeaking = false;
                btn.innerHTML = '<span>🔊 ฟังเสียงสรุป 60 วินาที</span>';
                status.textContent = 'หยุดชั่วคราว';
                return;
            }}

            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(voiceText);
            utterance.lang = 'th-TH';
            utterance.rate = 1.05;

            utterance.onstart = () => {{
                isSpeaking = true;
                btn.innerHTML = '<span>⏹️ หยุดเสียง</span>';
                status.textContent = 'กำลังบรรยายเสียง...';
            }};

            utterance.onend = () => {{
                isSpeaking = false;
                btn.innerHTML = '<span>🔊 ฟังเสียงสรุป 60 วินาที</span>';
                status.textContent = 'บรรยายจบแล้ว';
            }};

            utterance.onerror = () => {{
                isSpeaking = false;
                btn.innerHTML = '<span>🔊 ฟังเสียงสรุป 60 วินาที</span>';
                status.textContent = 'พร้อมบรรยาย';
            }};

            window.speechSynthesis.speak(utterance);
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
    readme_content = f"""# 🕵️‍♂️ MarketSherlock Cockpit (มาร์เก็ต เชอร์ล็อก)

> **Autonomous Morning Financial Intelligence & Interactive Cockpit Engine**  
> ปฏิบัติการเจาะลึกพลวัตการลงทุนรอบโลกและตลาดไทย ส่งตรงถึงคุณทุกเช้าเวลา 08:00 น.

[![Daily Dispatch](https://github.com/NutCodeLaw/market-sherlock/actions/workflows/daily_dispatch.yml/badge.svg)](https://github.com/NutCodeLaw/market-sherlock/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered By: Gemini 3.8 Flash](https://img.shields.io/badge/AI-Gemini%203.8%20Flash-blue)](https://ai.google.dev/)
[![Live Terminal Reader](https://img.shields.io/badge/Web%20Cockpit-GitHub%20Pages-success)](https://nutcodelaw.github.io/market-sherlock/)

---

## 📖 สรุปข่าวล่าสุด (Latest Morning Dispatch)
👉 **เปิดอ่านรายงานฉบับเต็ม:** [`LATEST.md`](./LATEST.md) หรือเปิด **[🌐 Interactive Web Cockpit](https://nutcodelaw.github.io/market-sherlock/)**

{raw_markdown}

---

## 🏛️ สถาปัตยกรรมระบบ (Architecture)
1. **Market Fetcher (`src/market_fetcher.py`)**: ดึงดัชนี SET, S&P 500, US 10Y Yield, Crude Oil, Gold, USD/THB ด้วย `yfinance` แบบ 100% Real-time
2. **AI Investigator (`src/ai_investigator.py`)**: ขับเคลื่อนด้วย Google Gemini 3.8 Flash พร้อมวิเคราะห์ Sentiment, Bull/Bear Ratio, Asset Allocation และ Bento Threat Levels
3. **State Tracker (`src/state_manager.py`)**: จดจำประเด็นข่าวย้อนหลัง 7 วัน ป้องกันการรายงานข่าวซ้ำ และตามติดความคืบหน้าของเรื่องราวอย่างต่อเนื่อง
4. **Interactive Cockpit (`src/reporter.py`)**: สร้างหน้า Web Cockpit สไตล์ Bloomberg/Finviz พร้อมเข็มไมล์ Sentiment, กล่องสี Heatmap, Bento แฟ้มคดี, ชักเย่อกระทิงหมี, และระบบเสียงบรรยายภาษาไทย
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
        
    # 4. Generate Pre-rendered Cockpit HTML
    rendered_html = build_prerendered_html(payload, raw_markdown)
    
    # Save to web/index.html and root index.html
    INDEX_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    with open(ROOT_INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(rendered_html)
