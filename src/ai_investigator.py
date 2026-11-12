"""
AI Investigator Module - Enhanced with Sentiment, Bento Threat Levels, Bull/Bear Ratio, and Asset Compass
"""
import os
import json
import re
from typing import Dict, Any, List
from google import genai
from src.config import GEMINI_MODELS, TRUSTED_SOURCES
from src.utils import get_now_bangkok, format_thai_date

def build_investigation_prompt(
    market_snapshot_text: str,
    raw_news: Dict[str, List[Dict[str, Any]]],
    history_context: str
) -> str:
    """Build detailed weekly investigative prompt with grounding news, 1W candlestick performance, and requirements."""
    now = get_now_bangkok()
    thai_date = format_thai_date(now)
    
    # Format Thai news articles
    thai_news_text = ""
    for idx, item in enumerate(raw_news.get("thai_articles", []), 1):
        thai_news_text += f"{idx}. [{item['source']}] {item['title']}\n   URL: {item['link']}\n"
        
    # Format Global news articles
    global_news_text = ""
    for idx, item in enumerate(raw_news.get("global_articles", []), 1):
        global_news_text += f"{idx}. [{item['source']}] {item['title']}\n   URL: {item['link']}\n"

    prompt = f"""คุณคือหัวหน้านักยุทธศาสตร์และนักวิเคราะห์ภาพใหญ่ (Macro & Weekly Candlestick Strategist) แห่ง 'MarketSherlock Weekly Cockpit'
ภารกิจ: สรุปภาพรวมและวิเคราะห์พลวัตการลงทุนรอบ 1 สัปดาห์ที่ผ่านมา (1-Week Retrospective) และวางหมากยุทธศาสตร์แท่งเทียนสัปดาห์ใหม่ สำหรับวันที่ {thai_date}

ข้อมูลผลตอบแทนรอบสัปดาห์ (1W Market Performance & Weekly Range):
{market_snapshot_text}

ประวัติการวิเคราะห์สัปดาห์ก่อนหน้า (ใช้ตรวจสอบความต่อเนื่องของภาพใหญ่):
{history_context}

ข่าวสารและพัฒนาการเชิงโครงสร้างสำคัญในรอบสัปดาห์:
[ข่าวตลาดไทย & หน่วยงานกำกับ (SET, BOT, สภาพัฒน์, BOI, ก.ล.ต.)]
{thai_news_text}

[ข่าวตลาดโลก & เศรษฐกิจมหภาค (Fed, Wall Street, บอนด์ยีลด์, น้ำมัน, ทองคำ)]
{global_news_text}

ตอบกลับเป็น JSON เท่านั้น (Strict JSON) ตามโครงสร้างนี้:
{{
  "market_sentiment": {{
    "score": 45,
    "label": "Neutral หรือ Fear หรือ Greed หรือ Extreme Fear หรือ Extreme Greed",
    "rationale": "สรุปอารมณ์ตลาดรอบสัปดาห์ 1 ประโยค (ประเมินจากบอนด์ยีลด์ ดอลลาร์ และสินทรัพย์เสี่ยง)"
  }},
  "bull_bear": {{
    "bull_pct": 45,
    "bear_pct": 55,
    "summary": "สรุปพลังกระทิง vs หมีรอบ 1 สัปดาห์ที่ผ่านมา 1 ประโยค",
    "bull_drivers": ["ปัจจัยหนุนรอบสัปดาห์ที่ 1", "ปัจจัยหนุนรอบสัปดาห์ที่ 2"],
    "bear_drivers": ["ปัจจัยกดดันรอบสัปดาห์ที่ 1", "ปัจจัยกดดันรอบสัปดาห์ที่ 2"]
  }},
  "asset_allocation": [
    {{"asset": "เงินสด & ตราสารหนี้สั้น", "pct": 40, "color": "#06b6d4"}},
    {{"asset": "หุ้นไทยคุณค่า & ปันผลสูง", "pct": 25, "color": "#10b981"}},
    {{"asset": "หุ้นโลก / สินทรัพย์เติบโต", "pct": 25, "color": "#3b82f6"}},
    {{"asset": "ทองคำ & สินทรัพย์ทางเลือก", "pct": 10, "color": "#f59e0b"}}
  ],
  "main_stories": [
    {{
      "threat_level": 5,
      "title": "พาดหัวประเด็นใหญ่ประจำสัปดาห์ (1W Major Theme)",
      "tldr": "สรุปหมัดเด็ด 1 สัปดาห์ที่ผ่านมาเกิดอะไรขึ้น 1 ประโยคสั้นๆ",
      "summary": "เนื้อหาเจาะลึกสิ่งที่เกิดขึ้นรอบ 7 วันที่ผ่านมา และความสำคัญเชิงโครงสร้าง 2-3 ประโยค",
      "takeaway": "Actionable Takeaway สำหรับการวางแผนแท่งเทียนสัปดาห์ใหม่",
      "continuity": "พัฒนาการสำคัญเมื่อเทียบกับสัปดาห์ก่อนหน้า",
      "source_name": "ชื่อแหล่งข่าวที่น่าเชื่อถือ",
      "source_url": "URL ข่าวจริงจากรายการข้างต้น"
    }}
  ],
  "market_briefs": [
    {{
      "tag": "#หมวดหมู่ เช่น #Bonds #Equities #Commodities #CentralBanks",
      "headline": "พาดหัวสั้นสรุปสัปดาห์",
      "text": "เนื้อหาพัฒนาการรอบ 1 สัปดาห์ 1 บรรทัด"
    }}
  ],
  "watchlist": [
    {{
      "time": "วัน/เวลา ในสัปดาห์ใหม่นี้ เช่น วันอังคาร 20:30 น. หรือ ปลายสัปดาห์",
      "event": "ตัวเลขเศรษฐกิจหรือวาระสำคัญที่จะกำหนดทิศทางแท่งเทียนสัปดาห์นี้"
    }}
  ],
  "beneficiaries": [
    "กลุ่มสินทรัพย์ที่แท่งเทียน 1W ได้เปรียบในสัปดาห์นี้"
  ],
  "risks": [
    "กลุ่มสินทรัพย์ที่แท่งเทียน 1W ส่อแววพักฐาน/เสี่ยงในสัปดาห์นี้"
  ],
  "strategies": [
    "กลยุทธ์หลักประจำสัปดาห์ (Weekly Strategy & Key Pivot Levels)"
  ]
}}
"""
    return prompt

def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Clean markdown formatting and extract JSON object."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception as e:
                print(f"[AIInvestigator] JSON regex parse failed: {e}")
        raise ValueError("Could not parse JSON from model output")

def run_investigation(
    market_snapshot_text: str,
    raw_news: Dict[str, List[Dict[str, Any]]],
    history_context: str
) -> Dict[str, Any]:
    """Run AI investigation through Gemini models with automatic fallback."""
    prompt = build_investigation_prompt(market_snapshot_text, raw_news, history_context)
    client = genai.Client()
    
    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            print(f"[AIInvestigator] Querying Gemini model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw_text = response.text
            parsed_data = extract_json_from_response(raw_text)
            print(f"[AIInvestigator] Successfully generated analysis using {model_name}")
            return parsed_data
        except Exception as e:
            print(f"[AIInvestigator] Model {model_name} encountered issue: {e}")
            last_error = e
            continue
            
    raise RuntimeError(f"All Gemini models failed: {last_error}")
