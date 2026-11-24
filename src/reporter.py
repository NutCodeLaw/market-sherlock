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
        f"# 🕵️‍♂️ MarketSherlock Weekly Cockpit — ยุทธศาสตร์การลงทุนรายสัปดาห์ ({thai_date})",
        f"*วิเคราะห์ภาพใหญ่และแท่งเทียน Timeframe Week • อัปเดตทุกเช้าวันเปิดตลาดสัปดาห์ใหม่ เวลา {time_str}*\n",
        "---",
        "",
        "## 📊 ผลตอบแทนรอบสัปดาห์ (1W Market Performance & Weekly Range)",
        "",
        data.get("snapshot_markdown", ""),
        "",
        "---",
        "",
        "## 🔍 3 มหาประเด็นชี้ขาดรอบสัปดาห์ (Weekly Major Themes)",
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
    lines.append("## 📅 วาระเศรษฐกิจต้องจับตาในสัปดาห์นี้ (Weekly Watchlist)")
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
    
    # 1. Market Sentiment Score (0 to 100 clamped)
    sentiment = data.get("market_sentiment", {})
    try:
        sent_score = max(0, min(100, int(float(sentiment.get("score", 50)))))
    except (TypeError, ValueError):
        sent_score = 50
    sent_label = html.escape(str(sentiment.get("label", "Neutral")))
    sent_rationale = html.escape(str(sentiment.get("rationale", "ตลาดอยู่ในช่วงจับตาทิศทางดอกเบี้ยโลกและกระแสเงินทุน")))
    
    # Needle degree for SVG speedometer (from -90deg to +90deg)
    # score 0 = -90deg, 50 = 0deg, 100 = 90deg
    needle_deg = ((sent_score / 100.0) * 180.0) - 90.0
    
    # Sentiment status color token
    if sent_score >= 60:
        sent_color = "var(--accent-green)"
    elif sent_score <= 40:
        sent_color = "var(--accent-red)"
    else:
        sent_color = "var(--accent-gold)"

    # 2. Asset Heatmap Grid (Finviz style with semantic classes across Light/Sepia/Dark)
    heatmap_cards_html = []
    for item in data.get("snapshot_items", []):
        pct = item.get("percent_change", 0.0)
        if pct > 0.5:
            tile_cls = "tile-up-strong"
        elif pct > 0.05:
            tile_cls = "tile-up"
        elif pct < -0.5:
            tile_cls = "tile-down-strong"
        elif pct < -0.05:
            tile_cls = "tile-down"
        else:
            tile_cls = "tile-flat"

        name = html.escape(str(item.get("name", "")))
        sym = html.escape(str(item.get("symbol", "")))
        price = html.escape(str(item.get("price_display", "")))
        chg = html.escape(str(item.get("change_display", "")))
        status = html.escape(str(item.get("status", "⚪")))

        card = f"""
        <div class="heatmap-tile {tile_cls}">
            <div class="heatmap-header">
                <span class="heatmap-name">{name}</span>
                <span class="heatmap-sym">{sym}</span>
            </div>
            <div class="heatmap-price tabular-nums">{price}</div>
            <div class="heatmap-chg tabular-nums">{status} {chg}</div>
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
    try:
        bull_pct = max(0, min(100, int(float(bb.get("bull_pct", 50)))))
    except (TypeError, ValueError):
        bull_pct = 50
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

    # Text for Audio Player (Voice narration — safe JSON serialization for inline <script>)
    plain_date = data.get("date_formatted", "") or data.get("date", "")
    plain_label = str(sentiment.get("label", "Neutral"))
    speech_text = f"รายงานสรุปยุทธศาสตร์เศรษฐกิจรอบสัปดาห์ มาร์เก็ตเชอร์ล็อก ประจำวันที่ {plain_date} อารมณ์ตลาดรอบสัปดาห์นี้อยู่ในเกณฑ์ {plain_label} คะแนน {sent_score} เต็ม 100 "
    for idx, story in enumerate(data.get("main_stories", [])[:3], 1):
        speech_text += f"ประเด็นที่ {idx}: {story.get('title', '')} จุดสำคัญคือ {story.get('tldr', '')}. "
    voice_text_json = json.dumps(speech_text, ensure_ascii=False).replace("</", r"<\/")

    escaped_raw_markdown = html.escape(raw_markdown)

    html_template = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <script>
        try {{
            var t = localStorage.getItem('hq_theme');
            if (!t) {{
                var legacy = localStorage.getItem('ms_theme');
                if (legacy === 'bloomberg' || legacy === 'slate') t = 'dark';
                else if (legacy === 'light' || legacy === 'sepia' || legacy === 'dark') t = legacy;
            }}
            var m = document.querySelector('meta[name="color-scheme"]');
            if (t === 'light' || t === 'sepia' || t === 'dark') {{
                document.documentElement.setAttribute('data-theme', t);
                if (m) m.content = (t === 'dark' ? 'dark' : 'light');
            }} else if (m) {{
                m.content = 'light dark';
            }}
        }} catch (e) {{}}
    </script>
    <title>🕵️‍♂️ MarketSherlock — Interactive Financial Cockpit</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Sarabun:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Modern Web 2026 Color Scheme + 3 Tailored Themes (Stripe Light / Oura Sepia / Raycast Dark) */
        :root {{
            color-scheme: light dark;
            --bg-base: #f6f9fc;
            --bg-surface: #ffffff;
            --bg-card: #f8fafc;
            --bg-inset: #eef2f7;
            --border: #e3e8ee;
            --text-main: #0d253d;
            --text-body: #273951;
            --text-muted: #64748d;
            --accent-primary: #533afd;
            --accent-gold: #b45309;
            --accent-cyan: #0284c7;
            --accent-green: #059669;
            --accent-red: #dc2626;
            --glass-bg: rgba(255, 255, 255, 0.88);
            --card-shadow: 0 4px 16px rgba(13, 37, 61, 0.06);
            --card-hover-shadow: 0 8px 24px rgba(13, 37, 61, 0.11);
            --scrollbar-thumb: #b4c0cf;
            --scrollbar-track: #eef2f7;
            --tone-cyan-bg: #e0f2fe;
            --tone-cyan-border: #bae6fd;
            --tone-cyan-ink: #0369a1;
            --tone-gold-bg: #fef3c7;
            --tone-gold-border: #fde68a;
            --tone-gold-ink: #92400e;
            --tile-up-strong-bg: #d1fae5;
            --tile-up-strong-border: #10b981;
            --tile-up-strong-ink: #065f46;
            --tile-up-bg: #ecfdf5;
            --tile-up-border: #6ee7b7;
            --tile-up-ink: #047857;
            --tile-down-strong-bg: #fee2e2;
            --tile-down-strong-border: #ef4444;
            --tile-down-strong-ink: #991b1b;
            --tile-down-bg: #fef2f2;
            --tile-down-border: #fca5a5;
            --tile-down-ink: #b91c1c;
            --tile-flat-bg: #f1f5f9;
            --tile-flat-border: #cbd5e1;
            --tile-flat-ink: #475569;
            --font-display: 'Plus Jakarta Sans', 'Sarabun', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}
        :root:has(> head > meta[name="color-scheme"][content="dark"]) {{ color-scheme: dark; }}
        :root:has(> head > meta[name="color-scheme"][content="light"]) {{ color-scheme: light; }}

        @media (prefers-color-scheme: dark) {{
            html:not([data-theme]) {{
                --bg-base: #07080a;
                --bg-surface: #0d0d0d;
                --bg-card: #121315;
                --bg-inset: #181a1d;
                --border: #242728;
                --text-main: #f4f4f6;
                --text-body: #cdcdcd;
                --text-muted: #9c9c9d;
                --accent-primary: #57c1ff;
                --accent-gold: #ffc533;
                --accent-cyan: #57c1ff;
                --accent-green: #59d499;
                --accent-red: #ff6161;
                --glass-bg: rgba(13, 13, 13, 0.88);
                --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
                --card-hover-shadow: 0 10px 28px rgba(0, 0, 0, 0.65);
                --scrollbar-thumb: #3c3e42;
                --scrollbar-track: #121315;
                --tone-cyan-bg: rgba(87, 193, 255, 0.14);
                --tone-cyan-border: rgba(87, 193, 255, 0.35);
                --tone-cyan-ink: #7dd3fc;
                --tone-gold-bg: rgba(255, 197, 51, 0.12);
                --tone-gold-border: rgba(255, 197, 51, 0.3);
                --tone-gold-ink: #fde68a;
                --tile-up-strong-bg: rgba(89, 212, 153, 0.22);
                --tile-up-strong-border: #59d499;
                --tile-up-strong-ink: #6ee7b7;
                --tile-up-bg: rgba(89, 212, 153, 0.11);
                --tile-up-border: #10b981;
                --tile-up-ink: #59d499;
                --tile-down-strong-bg: rgba(255, 97, 97, 0.22);
                --tile-down-strong-border: #ff6161;
                --tile-down-strong-ink: #fca5a5;
                --tile-down-bg: rgba(255, 97, 97, 0.11);
                --tile-down-border: #dc2626;
                --tile-down-ink: #ff6161;
                --tile-flat-bg: rgba(148, 163, 184, 0.12);
                --tile-flat-border: #475569;
                --tile-flat-ink: #cbd5e1;
            }}
        }}

        html[data-theme="sepia"] {{
            --bg-base: #f7f1e8;
            --bg-surface: #fffdf9;
            --bg-card: #f3ece0;
            --bg-inset: #eae1d2;
            --border: #e1dcd3;
            --text-main: #1c1b1a;
            --text-body: #3d3832;
            --text-muted: #6e685f;
            --accent-primary: #2a72de;
            --accent-gold: #af751b;
            --accent-cyan: #2a72de;
            --accent-green: #22663a;
            --accent-red: #c23321;
            --glass-bg: rgba(255, 253, 249, 0.9);
            --card-shadow: 0 4px 16px rgba(57, 34, 30, 0.07);
            --card-hover-shadow: 0 8px 24px rgba(57, 34, 30, 0.12);
            --scrollbar-thumb: #b7afa1;
            --scrollbar-track: #eae1d2;
            --tone-cyan-bg: #e7eef8;
            --tone-cyan-border: #bfd2ee;
            --tone-cyan-ink: #1e4e9b;
            --tone-gold-bg: #f6ecdb;
            --tone-gold-border: #dfd0b4;
            --tone-gold-ink: #7d4f0a;
            --tile-up-strong-bg: #e2eee5;
            --tile-up-strong-border: #2c6d42;
            --tile-up-strong-ink: #1c4a2b;
            --tile-up-bg: #edf5ef;
            --tile-up-border: #76a685;
            --tile-up-ink: #22663a;
            --tile-down-strong-bg: #f8e3df;
            --tile-down-strong-border: #c23321;
            --tile-down-strong-ink: #8b2012;
            --tile-down-bg: #fbf0ee;
            --tile-down-border: #dfa39b;
            --tile-down-ink: #b02a1a;
            --tile-flat-bg: #efe8dc;
            --tile-flat-border: #cfc6b8;
            --tile-flat-ink: #5b554d;
        }}

        html[data-theme="dark"] {{
            --bg-base: #07080a;
            --bg-surface: #0d0d0d;
            --bg-card: #121315;
            --bg-inset: #181a1d;
            --border: #242728;
            --text-main: #f4f4f6;
            --text-body: #cdcdcd;
            --text-muted: #9c9c9d;
            --accent-primary: #57c1ff;
            --accent-gold: #ffc533;
            --accent-cyan: #57c1ff;
            --accent-green: #59d499;
            --accent-red: #ff6161;
            --glass-bg: rgba(13, 13, 13, 0.88);
            --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
            --card-hover-shadow: 0 10px 28px rgba(0, 0, 0, 0.65);
            --scrollbar-thumb: #3c3e42;
            --scrollbar-track: #121315;
            --tone-cyan-bg: rgba(87, 193, 255, 0.14);
            --tone-cyan-border: rgba(87, 193, 255, 0.35);
            --tone-cyan-ink: #7dd3fc;
            --tone-gold-bg: rgba(255, 197, 51, 0.12);
            --tone-gold-border: rgba(255, 197, 51, 0.3);
            --tone-gold-ink: #fde68a;
            --tile-up-strong-bg: rgba(89, 212, 153, 0.22);
            --tile-up-strong-border: #59d499;
            --tile-up-strong-ink: #6ee7b7;
            --tile-up-bg: rgba(89, 212, 153, 0.11);
            --tile-up-border: #10b981;
            --tile-up-ink: #59d499;
            --tile-down-strong-bg: rgba(255, 97, 97, 0.22);
            --tile-down-strong-border: #ff6161;
            --tile-down-strong-ink: #fca5a5;
            --tile-down-bg: rgba(255, 97, 97, 0.11);
            --tile-down-border: #dc2626;
            --tile-down-ink: #ff6161;
            --tile-flat-bg: rgba(148, 163, 184, 0.12);
            --tile-flat-border: #475569;
            --tile-flat-ink: #cbd5e1;
        }}

        :root {{
            accent-color: var(--accent-primary);
            scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
        }}
        ::selection {{
            background: var(--accent-primary);
            color: #ffffff;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            overflow-y: auto;
            scroll-behavior: smooth;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-display);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            padding: 0 0 36px;
            overflow-x: hidden;
        }}

        .tabular-nums {{ font-variant-numeric: tabular-nums; }}

        :where(a:any-link, button, input, select):focus-visible {{
            outline: 3px solid var(--accent-primary);
            outline-offset: 2px;
        }}

        @media (prefers-reduced-motion: reduce) {{
            ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) {{
                animation: none !important;
            }}
            html {{ scroll-behavior: auto; }}
            .gauge-needle, .tug-bull-fill, .tug-bear-fill {{ transition: none !important; }}
        }}

        /* Sticky Top Glass Bar + Reading Progress */
        .top-utility-bar {{
            position: sticky;
            top: 0;
            z-index: 800;
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            margin-bottom: 18px;
        }}
        .top-utility-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 6px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}
        .util-brand {{
            font-size: 0.84rem;
            font-weight: 800;
            color: var(--text-main);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            min-width: 0;
        }}
        .util-actions {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-shrink: 0;
        }}
        .theme-seg-wrap {{
            display: inline-flex;
            align-items: center;
            gap: 2px;
            background: var(--bg-inset);
            border: 1px solid var(--border);
            padding: 2px;
            border-radius: 10px;
        }}
        .theme-seg-btn {{
            appearance: none;
            border: none;
            background: transparent;
            color: var(--text-muted);
            font-family: inherit;
            font-size: 0.74rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 8px;
            cursor: pointer;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .theme-seg-btn.is-active {{
            background: var(--bg-surface);
            color: var(--accent-primary);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.14);
        }}
        .util-search-btn {{
            appearance: none;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 5px 9px;
            border-radius: 10px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }}
        .util-search-btn:hover {{ border-color: var(--accent-primary); }}
        .kbd-hint {{
            font-size: 0.68rem;
            padding: 1px 4px;
            border-radius: 4px;
            background: var(--bg-inset);
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}
        .lbl-compact {{ display: none; }}
        @media (max-width: 540px) {{
            .lbl-full-sepia {{ display: none; }}
            .lbl-compact {{ display: inline; }}
            .kbd-hint {{ display: none; }}
            .util-brand-text {{ display: none; }}
            .theme-seg-btn {{ padding: 4px 7px; font-size: 0.72rem; }}
        }}
        @media (pointer: coarse) {{
            .theme-seg-btn, .util-search-btn {{ min-height: 40px; }}
        }}

        .reading-progress {{
            height: 3px;
            width: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-gold));
            transform-origin: 0 50%;
            transform: scaleX(0);
        }}
        @keyframes grow-progress {{
            from {{ transform: scaleX(0); }}
            to {{ transform: scaleX(1); }}
        }}
        @media (prefers-reduced-motion: no-preference) {{
            @supports (animation-timeline: scroll()) {{
                .reading-progress {{
                    animation: grow-progress auto linear;
                    animation-timeline: scroll(root);
                }}
            }}
        }}

        /* Native Quick Jump Modal Dialog */
        dialog#quick-jump-dialog {{
            margin: auto;
            width: min(560px, 92vw);
            max-height: 82dvh;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: var(--bg-surface);
            color: var(--text-main);
            padding: 0;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
            overflow: hidden;
        }}
        dialog#quick-jump-dialog:modal {{ overscroll-behavior: contain; }}
        dialog#quick-jump-dialog::backdrop {{
            background: rgba(15, 23, 42, 0.56);
            backdrop-filter: blur(4px);
        }}
        .qj-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            background: var(--bg-card);
        }}
        .qj-title {{ font-size: 0.92rem; font-weight: 800; color: var(--text-main); }}
        .qj-close {{
            appearance: none;
            background: var(--bg-inset);
            border: 1px solid var(--border);
            color: var(--text-main);
            width: 32px;
            height: 32px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 800;
        }}
        .qj-search-wrap {{ padding: 12px 16px 8px; }}
        .qj-input {{
            width: 100%;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.9rem;
        }}
        .qj-list {{
            max-height: 55dvh;
            overflow-y: auto;
            padding: 4px 12px 14px;
            display: grid;
            gap: 6px;
        }}
        .qj-item {{
            appearance: none;
            width: 100%;
            text-align: left;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 9px 12px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            font-family: inherit;
            font-size: 0.83rem;
        }}
        .qj-item:hover, .qj-item:focus-visible {{ border-color: var(--accent-primary); }}
        .qj-item-tag {{
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--tone-cyan-ink);
            background: var(--tone-cyan-bg);
            padding: 2px 7px;
            border-radius: 999px;
            flex-shrink: 0;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 16px;
        }}

        /* Header Cockpit */
        header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 18px;
            margin-bottom: 18px;
            gap: 14px;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-icon {{
            font-size: 2.1rem;
            background: var(--bg-inset);
            padding: 8px 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}

        .brand-title {{
            font-size: clamp(1.3rem, 3vw, 1.65rem);
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--text-main);
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
            background: var(--tone-cyan-bg);
            color: var(--tone-cyan-ink);
            border: 1px solid var(--tone-cyan-border);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.84rem;
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
            box-shadow: 0 0 8px var(--accent-green);
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
            margin-bottom: 22px;
            gap: 12px;
            box-shadow: var(--card-shadow);
        }}

        .audio-player-box {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .audio-btn {{
            background: var(--accent-primary);
            color: #ffffff;
            border: none;
            padding: 7px 14px;
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
            flex-wrap: wrap;
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
            transition: border-color 0.2s, background 0.2s;
        }}

        .btn:hover {{
            background: var(--bg-inset);
            border-color: var(--accent-primary);
        }}

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
            box-shadow: var(--card-shadow);
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
            background: var(--bg-inset);
            border: 1px solid var(--border);
        }}

        .sentiment-desc {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.45;
        }}

        /* Finviz Heatmap Tiles (Semantic Themes) */
        .heatmap-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
            gap: 10px;
        }}

        .heatmap-tile {{
            border: 1.5px solid var(--tile-flat-border);
            background: var(--tile-flat-bg);
            color: var(--text-main);
            border-radius: 12px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        .heatmap-tile.tile-up-strong {{ background: var(--tile-up-strong-bg); border-color: var(--tile-up-strong-border); }}
        .heatmap-tile.tile-up-strong .heatmap-chg {{ color: var(--tile-up-strong-ink); }}
        .heatmap-tile.tile-up {{ background: var(--tile-up-bg); border-color: var(--tile-up-border); }}
        .heatmap-tile.tile-up .heatmap-chg {{ color: var(--tile-up-ink); }}
        .heatmap-tile.tile-down-strong {{ background: var(--tile-down-strong-bg); border-color: var(--tile-down-strong-border); }}
        .heatmap-tile.tile-down-strong .heatmap-chg {{ color: var(--tile-down-strong-ink); }}
        .heatmap-tile.tile-down {{ background: var(--tile-down-bg); border-color: var(--tile-down-border); }}
        .heatmap-tile.tile-down .heatmap-chg {{ color: var(--tile-down-ink); }}
        .heatmap-tile.tile-flat {{ background: var(--tile-flat-bg); border-color: var(--tile-flat-border); }}
        .heatmap-tile.tile-flat .heatmap-chg {{ color: var(--tile-flat-ink); }}

        .heatmap-tile:hover {{
            transform: translateY(-2px);
            box-shadow: var(--card-hover-shadow);
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
            color: var(--text-main);
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
            color: var(--text-main);
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
            font-size: 1.18rem;
            font-weight: 800;
            margin: 28px 0 16px 0;
            color: var(--text-main);
            border-left: 4px solid var(--accent-gold);
            padding-left: 12px;
        }}

        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
            box-shadow: var(--card-shadow);
            transition: border-color 0.2s;
        }}

        .bento-card:hover {{
            border-color: var(--accent-primary);
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
            background: var(--tone-cyan-bg);
            color: var(--tone-cyan-ink);
            border: 1px solid var(--tone-cyan-border);
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
            color: var(--text-main);
            line-height: 1.4;
        }}

        .tldr-pill {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent-cyan);
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 0.88rem;
            color: var(--text-body);
            margin-bottom: 14px;
            line-height: 1.48;
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
            border-top: 1px solid var(--border);
            margin-bottom: 12px;
        }}

        .bento-deep-dive.open {{
            display: block;
        }}

        .bento-summary {{
            font-size: 0.9rem;
            color: var(--text-body);
            margin-bottom: 12px;
            line-height: 1.55;
        }}

        .takeaway-box {{
            background: var(--tone-gold-bg);
            border: 1px solid var(--tone-gold-border);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 12px;
        }}

        .takeaway-title {{
            font-size: 0.78rem;
            font-weight: 800;
            color: var(--tone-gold-ink);
            margin-bottom: 4px;
        }}

        .takeaway-content {{
            font-size: 0.86rem;
            color: var(--text-main);
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
            background: var(--tone-cyan-bg);
            border: 1px solid var(--tone-cyan-border);
            color: var(--tone-cyan-ink);
            text-decoration: none;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .source-pill:hover {{ text-decoration: underline; }}

        .toggle-btn {{
            background: var(--bg-inset);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            transition: background 0.2s;
        }}

        .toggle-btn:hover {{ border-color: var(--accent-primary); }}

        /* Module 3: Bull vs Bear Tug-of-War */
        .tug-war-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }}

        .tug-war-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .bull-pct-text {{ color: var(--accent-green); font-family: var(--font-mono); font-size: 1.05rem; font-variant-numeric: tabular-nums; }}
        .bear-pct-text {{ color: var(--accent-red); font-family: var(--font-mono); font-size: 1.05rem; font-variant-numeric: tabular-nums; }}

        .tug-war-bar {{
            height: 14px;
            border-radius: 9999px;
            display: flex;
            overflow: hidden;
            margin-bottom: 14px;
            background: var(--bg-inset);
        }}

        .tug-bull-fill {{ background: linear-gradient(90deg, #059669, #34d399); transition: width 1s; }}
        .tug-bear-fill {{ background: linear-gradient(90deg, #f87171, #dc2626); transition: width 1s; }}

        .tug-war-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}

        .army-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
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
            color: var(--text-body);
            line-height: 1.55;
        }}

        /* Module 4: Asset Allocation Bar */
        .alloc-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }}

        .alloc-bar {{
            height: 20px;
            border-radius: 9999px;
            display: flex;
            overflow: hidden;
            margin: 12px 0 14px 0;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        }}

        .alloc-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            font-size: 0.85rem;
            color: var(--text-body);
            font-variant-numeric: tabular-nums;
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
            box-shadow: var(--card-shadow);
        }}

        .brief-tag {{
            font-size: 0.7rem;
            font-weight: 700;
            font-family: var(--font-mono);
            background: var(--tone-gold-bg);
            border: 1px solid var(--tone-gold-border);
            color: var(--tone-gold-ink);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .brief-headline {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--text-main);
            margin: 5px 0 3px;
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
            box-shadow: var(--card-shadow);
        }}

        .strategy-list {{
            list-style: none;
            font-size: 0.86rem;
            color: var(--text-body);
        }}

        .strategy-list li {{
            margin-bottom: 8px;
            line-height: 1.48;
        }}
        .strategy-highlight {{
            font-size: 0.88rem;
            color: var(--text-main);
            line-height: 1.5;
        }}

        footer {{
            margin-top: 44px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.82rem;
        }}

        /* White-Paper Print Normalization */
        @media print {{
            html, body {{
                color-scheme: light !important;
                background: #ffffff !important;
                color: #0f172a !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
            .no-print, dialog, .controls-bar, .toggle-btn {{ display: none !important; }}
            .bento-deep-dive {{ display: block !important; }}
            .bento-card, .sentiment-card, .tug-war-box, .alloc-card, .brief-item, .strategy-box {{
                background: #ffffff !important;
                color: #0f172a !important;
                border-color: #cbd5e1 !important;
                box-shadow: none !important;
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <nav class="top-utility-bar no-print" aria-label="แถบเครื่องมือและสลับธีมสี">
        <div class="top-utility-inner">
            <div class="util-brand">🕵️‍♂️ <span class="util-brand-text">MarketSherlock Cockpit</span></div>
            <div class="util-actions">
                <div class="theme-seg-wrap" role="group" aria-label="เลือกโหมดสีหน้าจอ">
                    <button type="button" class="theme-seg-btn" data-theme-btn="light" aria-pressed="false" onclick="setTheme('light')">☀️ สว่าง</button>
                    <button type="button" class="theme-seg-btn" data-theme-btn="sepia" aria-pressed="false" onclick="setTheme('sepia')">📖 <span class="lbl-full-sepia">ถนอมสายตา</span><span class="lbl-compact">ถนอม</span></button>
                    <button type="button" class="theme-seg-btn" data-theme-btn="dark" aria-pressed="false" onclick="setTheme('dark')">🌙 มืด</button>
                </div>
                <button type="button" id="quick-jump-btn" class="util-search-btn" aria-label="ค้นหาและกระโดดหมวด">🔍 <kbd class="kbd-hint">⌘K</kbd></button>
            </div>
        </div>
        <div id="reading-progress" class="reading-progress" aria-hidden="true"></div>
    </nav>

    <div class="container">
        <!-- Header -->
        <header>
            <div class="brand">
                <div class="brand-icon">🕵️‍♂️</div>
                <div>
                    <h1 class="brand-title">MarketSherlock Weekly Cockpit</h1>
                    <div class="brand-sub">ยุทธศาสตร์การลงทุนและวิเคราะห์แท่งเทียนรอบสัปดาห์ (Timeframe Week)</div>
                </div>
            </div>
            <div class="header-meta">
                <div class="time-badge tabular-nums">
                    <span class="status-dot"></span>
                    <span>สัปดาห์ {html.escape(data.get("week_id", ""))} • {date_display}</span>
                </div>
            </div>
        </header>

        <!-- Controls & Audio Narration Bar -->
        <div class="controls-bar no-print">
            <div class="audio-player-box">
                <button type="button" class="audio-btn" id="play-voice-btn" onclick="playVoiceSummary()">
                    <span>🔊 ฟังเสียงวิเคราะห์สัปดาห์นี้ 60 วินาที</span>
                </button>
                <span class="audio-status" id="audio-status-text">พร้อมบรรยาย</span>
            </div>
            <div class="theme-buttons">
                <button type="button" class="btn" onclick="copyMarkdown()">📋 Copy MD</button>
            </div>
        </div>

        <!-- 1. Market Sentiment Gauge + Finviz Heatmap Grid -->
        <div id="sec-sentiment" class="cockpit-top-grid">
            <!-- Sentiment Gauge -->
            <div class="sentiment-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 4px;">🧭 MARKET SENTIMENT</div>
                <svg class="gauge-svg" viewBox="0 0 200 110">
                    <!-- Gauge Arc -->
                    <path d="M 20 95 A 80 80 0 0 1 180 95" fill="none" stroke="var(--border)" stroke-width="16" stroke-linecap="round"/>
                    <!-- Color Sections -->
                    <path d="M 20 95 A 80 80 0 0 1 65 38" fill="none" stroke="#ef4444" stroke-width="16" stroke-linecap="round"/>
                    <path d="M 68 35 A 80 80 0 0 1 132 35" fill="none" stroke="#f59e0b" stroke-width="16"/>
                    <path d="M 135 38 A 80 80 0 0 1 180 95" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round"/>
                    <!-- Needle -->
                    <g class="gauge-needle" style="transform: rotate({needle_deg}deg);">
                        <polygon points="98,95 102,95 100,24" fill="var(--text-main)"/>
                        <circle cx="100" cy="95" r="7" fill="{sent_color}"/>
                    </g>
                </svg>
                <div class="sentiment-val tabular-nums" style="color: {sent_color};">{sent_score}</div>
                <div class="sentiment-tag" style="color: {sent_color};">{sent_label}</div>
                <div class="sentiment-desc">{sent_rationale}</div>
            </div>

            <!-- Heatmap Tiles -->
            <div id="sec-heatmap" class="heatmap-grid">
{heatmap_rendered}
            </div>
        </div>

        <!-- 2. Bento Grid Crime Files (3 Main Stories) -->
        <div id="sec-stories" class="section-header">📂 3 แฟ้มคดีสืบสวนเด่น (Investigative Crime Files)</div>
        <div class="bento-grid">
{bento_rendered}
        </div>

        <!-- 3. Bull vs Bear Tug-of-War -->
        <div id="sec-tugwar" class="section-header">🐂⚔️🐻 Bull vs Bear Tug-of-War (สมรภูมิกระทิงปะทะหมี)</div>
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
        <div id="sec-alloc" class="section-header">🍰 Sherlock’s Weekly Asset Compass (สูตรจัดสัดส่วนพอร์ตสัปดาห์นี้)</div>
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
        <div id="sec-briefs" class="bottom-grid">
            <div>
                <div class="section-header" style="margin-top: 0;">⚡ Market Briefs รอบตลาด</div>
{briefs_rendered}
            </div>
            <div>
                <div id="sec-watchlist" class="section-header" style="margin-top: 0;">📅 Weekly Watchlist &amp; กลยุทธ์</div>
                <div class="strategy-box">
                    <div style="font-weight: 800; color: var(--accent-cyan); margin-bottom: 8px;">วาระสำคัญสัปดาห์นี้:</div>
{watchlist_rendered}
                    <div style="border-top: 1px solid var(--border); margin: 12px 0;"></div>
                    <div style="font-weight: 800; color: var(--accent-gold); margin-bottom: 6px;">💡 คำแนะนำกลยุทธ์หลัก:</div>
                    <div class="strategy-highlight">{html.escape(data.get('strategies', ['เน้น Selective Value'])[0] if data.get('strategies') else '')}</div>
                </div>
            </div>
        </div>

        <footer>
            MarketSherlock Cockpit v2.3-HQ • ขับเคลื่อนด้วย Google Gemini 3.5 Flash-Lite &amp; Python Autonomous Pipeline • แหล่งข่าว: Bloomberg, Reuters, FT, WSJ, ก.ล.ต., ธปท., ตลาดหลักทรัพย์ฯ, สภาพัฒน์
        </footer>
    </div>

    <!-- Hidden Raw Markdown for Copy Button -->
    <textarea id="raw-markdown-data" style="display:none;">{escaped_raw_markdown}</textarea>

    <dialog id="quick-jump-dialog" closedby="any" aria-labelledby="qj-dialog-title">
        <div class="qj-head">
            <div id="qj-dialog-title" class="qj-title">🔍 ค้นหาและกระโดดหมวด (MarketSherlock)</div>
            <button type="button" id="qj-close-btn" class="qj-close" aria-label="ปิดหน้าต่างค้นหา">✕</button>
        </div>
        <div class="qj-search-wrap">
            <input type="search" id="qj-search-input" class="qj-input" placeholder="พิมพ์ชื่อสินทรัพย์, แฟ้มคดี, กลยุทธ์, หรือเลือกธีมสี..." autocomplete="off">
        </div>
        <div id="qj-results-list" class="qj-list"></div>
    </dialog>

    <!-- Client-side Interactive Logic -->
    <script>
        function toggleDetails(id, btn) {{
            const el = document.getElementById(id);
            if (!el) return;
            if (el.classList.contains('open')) {{
                el.classList.remove('open');
                if (btn) {{
                    btn.querySelector('span').textContent = '🔎 เจาะลึกแฟ้มคดี';
                    btn.querySelector('.arrow-icon').textContent = '▼';
                }}
            }} else {{
                el.classList.add('open');
                if (btn) {{
                    btn.querySelector('span').textContent = '📁 ย่อเก็บแฟ้ม';
                    btn.querySelector('.arrow-icon').textContent = '▲';
                }}
            }}
        }}

        function getEffectiveTheme() {{
            try {{
                let saved = localStorage.getItem('hq_theme');
                if (!saved) {{
                    const leg = localStorage.getItem('ms_theme');
                    if (leg === 'bloomberg' || leg === 'slate') saved = 'dark';
                    else if (leg === 'light' || leg === 'sepia' || leg === 'dark') saved = leg;
                }}
                if (saved === 'light' || saved === 'sepia' || saved === 'dark') return saved;
            }} catch (e) {{}}
            return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
        }}

        function syncThemeUI() {{
            const active = getEffectiveTheme();
            document.querySelectorAll('[data-theme-btn]').forEach((btn) => {{
                const isMatch = btn.getAttribute('data-theme-btn') === active;
                btn.classList.toggle('is-active', isMatch);
                btn.setAttribute('aria-pressed', String(isMatch));
            }});
        }}

        function setTheme(theme) {{
            if (theme === 'bloomberg' || theme === 'slate') theme = 'dark';
            if (!['light', 'sepia', 'dark'].includes(theme)) theme = 'light';
            const apply = () => {{
                document.documentElement.setAttribute('data-theme', theme);
                const metaCS = document.querySelector('meta[name="color-scheme"]');
                if (metaCS) metaCS.content = (theme === 'dark' ? 'dark' : 'light');
                try {{ localStorage.setItem('hq_theme', theme); }} catch (e) {{}}
                syncThemeUI();
            }};
            if (typeof document.startViewTransition === 'function') {{
                document.startViewTransition(apply);
            }} else {{
                apply();
            }}
        }}

        window.addEventListener('storage', (e) => {{
            if (e.key === 'hq_theme') {{
                const v = e.newValue;
                const metaCS = document.querySelector('meta[name="color-scheme"]');
                if (v === 'light' || v === 'sepia' || v === 'dark') {{
                    document.documentElement.setAttribute('data-theme', v);
                    if (metaCS) metaCS.content = (v === 'dark' ? 'dark' : 'light');
                }} else {{
                    document.documentElement.removeAttribute('data-theme');
                    if (metaCS) metaCS.content = 'light dark';
                }}
                syncThemeUI();
            }}
        }});

        if (window.matchMedia) {{
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {{
                let saved = null;
                try {{ saved = localStorage.getItem('hq_theme'); }} catch (e) {{}}
                if (!saved) syncThemeUI();
            }});
        }}
        syncThemeUI();

        if (!CSS.supports('animation-timeline', 'scroll()')) {{
            const progEl = document.getElementById('reading-progress');
            const onScroll = () => {{
                if (!progEl) return;
                const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
                const pct = Math.max(0, Math.min(1, window.scrollY / max));
                progEl.style.transform = `scaleX(${{pct}})`;
            }};
            window.addEventListener('scroll', onScroll, {{ passive: true }});
            onScroll();
        }}

        function copyMarkdown() {{
            const md = document.getElementById('raw-markdown-data').value;
            navigator.clipboard.writeText(md).then(() => {{
                alert("📋 คัดลอกรายงานสรุป Markdown เรียบร้อยแล้ว!");
            }});
        }}

        // Native Browser Voice Narration
        let isSpeaking = false;
        const voiceText = {voice_text_json};

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
                btn.innerHTML = '<span>🔊 ฟังเสียงวิเคราะห์สัปดาห์นี้ 60 วินาที</span>';
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
                btn.innerHTML = '<span>🔊 ฟังเสียงวิเคราะห์สัปดาห์นี้ 60 วินาที</span>';
                status.textContent = 'บรรยายจบแล้ว';
            }};

            utterance.onerror = () => {{
                isSpeaking = false;
                btn.innerHTML = '<span>🔊 ฟังเสียงวิเคราะห์สัปดาห์นี้ 60 วินาที</span>';
                status.textContent = 'พร้อมบรรยาย';
            }};

            window.speechSynthesis.speak(utterance);
        }}

        // Quick Jump Native <dialog> Palette
        (function initQuickJump() {{
            const dlg = document.getElementById('quick-jump-dialog');
            const btn = document.getElementById('quick-jump-btn');
            const closeBtn = document.getElementById('qj-close-btn');
            const input = document.getElementById('qj-search-input');
            const list = document.getElementById('qj-results-list');
            if (!dlg || !btn || !input || !list) return;

            if (!('closedBy' in HTMLDialogElement.prototype)) {{
                dlg.addEventListener('click', (e) => {{
                    if (e.target !== dlg) return;
                    const r = dlg.getBoundingClientRect();
                    if (r.top <= e.clientY && e.clientY <= r.top + r.height && r.left <= e.clientX && e.clientX <= r.left + r.width) return;
                    dlg.close();
                }});
            }}

            const items = [
                {{ label: '☀️ สลับเป็นโหมดสว่าง (Stripe Daylight)', tag: 'Theme', action: () => setTheme('light') }},
                {{ label: '📖 สลับเป็นโหมดถนอมสายตา (Oura Paper)', tag: 'Theme', action: () => setTheme('sepia') }},
                {{ label: '🌙 สลับเป็นโหมดมืด (Raycast Dark)', tag: 'Theme', action: () => setTheme('dark') }},
                {{ label: '🧭 Market Sentiment & Heatmap (6 สินทรัพย์)', tag: 'Section', action: () => document.getElementById('sec-sentiment')?.scrollIntoView({{ behavior: 'smooth' }}) }},
                {{ label: '🐂⚔️🐻 Bull vs Bear Tug-of-War', tag: 'Section', action: () => document.getElementById('sec-tugwar')?.scrollIntoView({{ behavior: 'smooth' }}) }},
                {{ label: '🍰 Sherlock Asset Compass (จัดสัดส่วนพอร์ต)', tag: 'Section', action: () => document.getElementById('sec-alloc')?.scrollIntoView({{ behavior: 'smooth' }}) }},
                {{ label: '📅 Weekly Watchlist & กลยุทธ์หลัก', tag: 'Section', action: () => document.getElementById('sec-watchlist')?.scrollIntoView({{ behavior: 'smooth' }}) }},
            ];

            document.querySelectorAll('.heatmap-tile').forEach((tile) => {{
                const nm = tile.querySelector('.heatmap-name')?.textContent?.trim() || '';
                const ch = tile.querySelector('.heatmap-chg')?.textContent?.trim() || '';
                if (nm) {{
                    items.push({{
                        label: `📊 ${{nm}} (${{ch}})`,
                        tag: 'Asset',
                        action: () => tile.scrollIntoView({{ behavior: 'smooth', block: 'center' }})
                    }});
                }}
            }});

            document.querySelectorAll('.bento-card').forEach((card) => {{
                const tEl = card.querySelector('.bento-title');
                const deepEl = card.querySelector('.bento-deep-dive');
                const tBtn = card.querySelector('.toggle-btn');
                if (tEl) {{
                    items.push({{
                        label: `📂 ${{tEl.textContent.trim()}}`,
                        tag: 'Story',
                        action: () => {{
                            if (deepEl && !deepEl.classList.contains('open')) toggleDetails(deepEl.id, tBtn);
                            card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        }}
                    }});
                }}
            }});

            let filtered = items;
            function renderList(q) {{
                const norm = (q || '').trim().toLowerCase();
                filtered = norm ? items.filter(it => it.label.toLowerCase().includes(norm) || it.tag.toLowerCase().includes(norm)) : items.slice(0, 16);
                list.replaceChildren();
                filtered.forEach((it) => {{
                    const b = document.createElement('button');
                    b.type = 'button';
                    b.className = 'qj-item';
                    const spLabel = document.createElement('span');
                    spLabel.textContent = it.label;
                    const spTag = document.createElement('span');
                    spTag.className = 'qj-item-tag';
                    spTag.textContent = it.tag;
                    b.appendChild(spLabel);
                    b.appendChild(spTag);
                    b.addEventListener('click', () => {{ dlg.close(); it.action(); }});
                    list.appendChild(b);
                }});
            }}

            function openDlg() {{
                input.value = '';
                renderList('');
                dlg.showModal();
                setTimeout(() => input.focus(), 40);
            }}

            btn.addEventListener('click', openDlg);
            if (closeBtn) closeBtn.addEventListener('click', () => dlg.close());
            input.addEventListener('input', () => renderList(input.value));
            input.addEventListener('keydown', (e) => {{
                if (e.key === 'Enter' && filtered.length > 0) {{
                    e.preventDefault();
                    dlg.close();
                    filtered[0].action();
                }}
            }});
            document.addEventListener('keydown', (e) => {{
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {{
                    const tag = document.activeElement ? document.activeElement.tagName : '';
                    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
                    e.preventDefault();
                    if (dlg.open) dlg.close(); else openDlg();
                }}
            }});
        }})();
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

> **Autonomous Weekly Financial Intelligence & Interactive Cockpit Engine**  
> ปฏิบัติการเจาะลึกพลวัตการลงทุนรอบโลกและตลาดไทย (Timeframe Week) ส่งตรงถึงคุณทุกเช้าวันจันทร์ เวลา 08:00 น.

[![Weekly Dispatch](https://github.com/NutCodeLaw/market-sherlock/actions/workflows/daily_dispatch.yml/badge.svg)](https://github.com/NutCodeLaw/market-sherlock/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered By: Gemini 3.5 Flash-Lite](https://img.shields.io/badge/AI-Gemini%203.5%20Flash--Lite-blue)](https://ai.google.dev/)
[![Live Terminal Reader](https://img.shields.io/badge/Web%20Cockpit-GitHub%20Pages-success)](https://nutcodelaw.github.io/market-sherlock/)

---

## 📖 สรุปยุทธศาสตร์รอบสัปดาห์ล่าสุด (Latest Weekly Dispatch)
👉 **เปิดอ่านรายงานฉบับเต็ม:** [`LATEST.md`](./LATEST.md) หรือเปิด **[🌐 Interactive Web Cockpit](https://nutcodelaw.github.io/market-sherlock/)**

{raw_markdown}

---

## 🏛️ สถาปัตยกรรมระบบ (Architecture)
1. **Market Fetcher (`src/market_fetcher.py`)**: ดึงดัชนี SET, S&P 500, US 10Y Yield, Crude Oil, Gold, USD/THB ด้วย `yfinance` รอบ 1W Candlestick
2. **AI Investigator (`src/ai_investigator.py`)**: ขับเคลื่อนด้วย Google Gemini 3.5 Flash-Lite (fallback 3.8/3.6 Flash) พร้อมวิเคราะห์ Sentiment, Bull/Bear Ratio, Asset Allocation และ Bento Threat Levels
3. **State & Holiday Guard (`src/state_manager.py`, `src/holiday_guard.py`)**: จดจำประเด็นสัปดาห์ก่อนหน้า ป้องกันการรายงานซ้ำ และตรวจสอบวันหยุดตลาดหลักทรัพย์ฯ (SET) เพื่อเลื่อนรันเป็นวันเปิดตลาดถัดไปอัตโนมัติ (Holiday Rollover)
4. **Interactive Cockpit (`src/reporter.py`)**: สร้างหน้า Web Cockpit สไตล์ Bloomberg/Finviz พร้อมเข็มไมล์ Sentiment, กล่องสี Heatmap, Bento แฟ้มคดี, ชักเย่อกระทิงหมี, และระบบเสียงบรรยายภาษาไทย
5. **Autonomous Cron (`.github/workflows/daily_dispatch.yml`)**: ทำงานบน GitHub Actions ฟรี 100% รันตรงเวลา **ทุกวันจันทร์ 08:00 น. (01:00 UTC)** พร้อมส่งสรุป Fast-Bite เข้า Telegram `-1003712039650`

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
