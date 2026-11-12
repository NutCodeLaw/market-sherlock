"""
MarketSherlock - Main Entrypoint & Weekly Orchestrator (1W Candlestick Strategy)
"""
import sys
import argparse
from datetime import datetime
from src.utils import get_now_bangkok, format_thai_date, get_iso_date
from src.market_fetcher import get_market_snapshot
from src.news_curator import get_curated_raw_news
from src.state_manager import (
    get_recent_history_context,
    get_current_week_identifier,
    is_current_week_already_reported,
    append_weekly_topics
)
from src.ai_investigator import run_investigation
from src.reporter import generate_markdown_report, save_all_reports

def main():
    parser = argparse.ArgumentParser(description="MarketSherlock Weekly Intelligence Engine")
    parser.add_argument("--preview", action="store_true", help="Print report to console without saving")
    parser.add_argument("--force", action="store_true", help="Force run even if this week is already reported")
    args = parser.parse_args()

    now = get_now_bangkok()
    thai_date = format_thai_date(now)
    iso_date = get_iso_date(now)
    current_week = get_current_week_identifier(now)
    
    print("=" * 65)
    print(f"🕵️‍♂️ MarketSherlock Weekly Intelligence Cockpit")
    print(f"📅 ประจำสัปดาห์: {current_week} ({thai_date})")
    print(f"⏰ เวลาประมวลผล: {now.strftime('%H:%M:%S')} (Asia/Bangkok)")
    print("=" * 65)
    
    # 0. Check Weekly Schedule Guard
    if not args.force and is_current_week_already_reported():
        print(f"\n[Scheduler] 🛡️ สัปดาห์ {current_week} ได้รับการวิเคราะห์เรียบร้อยแล้ว")
        print(f"   -> ระบบจะตื่นมาวิเคราะห์ใหม่อีกครั้งในวันจันทร์ถัดไป เวลา 08:00 น.")
        print(f"   (หากต้องการรันซ้ำเพื่อทดสอบ ให้ใช้คำสั่ง: python main.py --force)")
        sys.exit(0)

    # 1. Fetch Weekly Market Snapshot (1W Candlestick & Weekly Range)
    print("\n[1/5] 📊 กำลังดึงผลตอบแทนแท่งเทียนรอบสัปดาห์ (1W High-Low, % Change)...")
    market_data = get_market_snapshot()
    print(f"   -> คำนวณผลตอบแทนรอบ 1 สัปดาห์สำเร็จ {len(market_data['items'])} สินทรัพย์")
    
    # 2. Curate News Feeds
    print("\n[2/5] 📰 กำลังรวบรวมพัฒนาการเชิงโครงสร้างสำคัญรอบ 1 สัปดาห์ที่ผ่านมา...")
    raw_news = get_curated_raw_news()
    print(f"   -> ตรวจสอบข่าวสารตลาดไทย {len(raw_news['thai_articles'])} ข่าว / ตลาดโลก {len(raw_news['global_articles'])} ข่าว")
    
    # 3. Check State & History
    print("\n[3/5] 🧠 กำลังตรวจสอบประวัติความต่อเนื่องภาพใหญ่ (Weekly Retrospective)...")
    history_context = get_recent_history_context(days=14)
    
    # 4. Run AI Investigation
    print("\n[4/5] 🔬 กำลังวิเคราะห์ยุทธศาสตร์ Timeframe Week ด้วย Google Gemini 3.8 Flash...")
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
        "week_id": current_week,
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
    print("\n[5/5] 📝 กำลังจัดพิมพ์ Weekly Cockpit ลง LATEST.md, README.md, archives/ และ Web Cockpit...")
    markdown_report = generate_markdown_report(payload)
    
    if args.preview:
        print("\n" + "=" * 65)
        print(markdown_report)
        print("=" * 65)
    else:
        save_all_reports(payload, markdown_report)
        
        # Save week topics to history
        topics_to_save = [
            {"title": s.get("title", ""), "theme": s.get("continuity", "")}
            for s in analysis_data.get("main_stories", [])
        ]
        append_weekly_topics(current_week, iso_date, topics_to_save)
        
        # Telegram dispatch is intentionally disabled per user request
        # send_telegram_briefing(payload)
        
        print("\n🎉 จัดทำยุทธศาสตร์ประจำสัปดาห์เสร็จสมบูรณ์เรียบร้อยแล้ว!")
        print("📁 ไฟล์ที่สร้าง/อัปเดต:")
        print("   - LATEST.md (สรุปประจำสัปดาห์ฉบับล่าสุด)")
        print(f"   - archives/{iso_date}.md (บันทึกคลังประวัติศาสตร์)")
        print("   - README.md (หน้าแรกของ GitHub Repository)")
        print("   - web/index.html & index.html (หน้าจอ Weekly Web Cockpit สวยหรู)")

if __name__ == "__main__":
    main()
