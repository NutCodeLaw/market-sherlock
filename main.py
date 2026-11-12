"""
MarketSherlock - Main Entrypoint & Autonomous Orchestrator
"""
import sys
import argparse
from datetime import datetime
from src.utils import get_now_bangkok, format_thai_date, get_iso_date
from src.market_fetcher import get_market_snapshot
from src.news_curator import get_curated_raw_news
from src.state_manager import get_recent_history_context, append_daily_topics
from src.ai_investigator import run_investigation
from src.reporter import generate_markdown_report, save_all_reports
from src.notifier import send_telegram_briefing

def main():
    parser = argparse.ArgumentParser(description="MarketSherlock Morning Intelligence Engine")
    parser.add_argument("--preview", action="store_true", help="Print report to console without saving")
    args = parser.parse_args()

    now = get_now_bangkok()
    thai_date = format_thai_date(now)
    iso_date = get_iso_date(now)
    
    print("=" * 60)
    print(f"🕵️‍♂️ MarketSherlock Morning Dispatch Engine")
    print(f"📅 ประจำวันที่: {thai_date} ({now.strftime('%H:%M:%S')} Asia/Bangkok)")
    print("=" * 60)
    
    # 1. Fetch Market Snapshot
    print("\n[1/5] 📊 กำลังดึงข้อมูลดัชนีตลาดสำคัญแบบ Real-time (SET, S&P500, US10Y, Oil, Gold, FX)...")
    market_data = get_market_snapshot()
    print(f"   -> ดึงข้อมูลสำเร็จ {len(market_data['items'])} รายการ")
    
    # 2. Curate News Feeds
    print("\n[2/5] 📰 กำลังรวบรวมข่าวสารรอบ 24 ชั่วโมงจากแหล่งที่เชื่อถือได้ (Thai + Global)...")
    raw_news = get_curated_raw_news()
    print(f"   -> พบข่าวตลาดไทย {len(raw_news['thai_articles'])} ข่าว / ข่าวตลาดโลก {len(raw_news['global_articles'])} ข่าว")
    
    # 3. Check State & History
    print("\n[3/5] 🧠 กำลังตรวจสอบประวัติข่าวย้อนหลัง (Anti-Duplication & Continuity Engine)...")
    history_context = get_recent_history_context(days=7)
    
    # 4. Run AI Investigation
    print("\n[4/5] 🔬 กำลังสืบสวนและวิเคราะห์นัยเชิงกลยุทธ์ด้วย Google Gemini...")
    try:
        analysis_data = run_investigation(
            market_snapshot_text=market_data["markdown_table"],
            raw_news=raw_news,
            history_context=history_context
        )
    except Exception as e:
        print(f"\n❌ การวิเคราะห์ล้มเหลว: {e}")
        sys.exit(1)
        
    # Combine payload
    payload = {
        "date": iso_date,
        "date_formatted": thai_date,
        "time": now.strftime("%H:%M น."),
        "snapshot_markdown": market_data["markdown_table"],
        "snapshot_items": market_data["items"],
        "market_sentiment": analysis_data.get("market_sentiment", {}),
        "bull_bear": analysis_data.get("bull_bear", {}),
        "asset_allocation": analysis_data.get("asset_allocation", []),
        "main_stories": analysis_data.get("main_stories", []),
        "market_briefs": analysis_data.get("market_briefs", []),
        "watchlist": analysis_data.get("watchlist", []),
        "beneficiaries": analysis_data.get("beneficiaries", []),
        "risks": analysis_data.get("risks", []),
        "strategies": analysis_data.get("strategies", [])
    }
    
    # 5. Generate and Save Reports
    print("\n[5/5] 📝 กำลังจัดพิมพ์รายงานลง LATEST.md, README.md, archives/ และ Web Reader...")
    markdown_report = generate_markdown_report(payload)
    
    if args.preview:
        print("\n" + "=" * 60)
        print(markdown_report)
        print("=" * 60)
    else:
        save_all_reports(payload, markdown_report)
        
        # Save new topics to history
        topics_to_save = [
            {"title": s.get("title", ""), "theme": s.get("continuity", "")}
            for s in analysis_data.get("main_stories", [])
        ]
        append_daily_topics(iso_date, topics_to_save)
        
        # Send Telegram notification if configured
        send_telegram_briefing(payload)
        
        print("\n🎉 จัดทำรายงานเสร็จสมบูรณ์เรียบร้อยแล้ว!")
        print("📁 ไฟล์ที่สร้าง/อัปเดต:")
        print("   - LATEST.md (สรุปฉบับล่าสุดสำหรับเปิดอ่านเร็ว)")
        print(f"   - archives/{iso_date}.md (บันทึกคลังประวัติศาสตร์)")
        print("   - README.md (หน้าแรกของ GitHub Repository)")
        print("   - web/index.html (หน้าจอ Web Terminal Reader สวยงาม)")

if __name__ == "__main__":
    main()
