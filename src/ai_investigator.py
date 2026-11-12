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
    """Build detailed investigative prompt with grounding news, state context, and requirements."""
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

    prompt = f"""คุณคือหัวหน้านักสืบและหัวหน้านักกลยุทธ์การลงทุนอาวุโสแห่ง 'MarketSherlock Financial Cockpit'
ภารกิจ: วิเคราะห์ข่าวสารรอบ 24 ชั่วโมง และข้อมูลตลาดสด เพื่อสร้างรายงานประจำวันที่ {thai_date}

ข้อมูลตัวเลขตลาดล่าสุด (Market Snapshot):
{market_snapshot_text}

ประวัติข่าวเด่น 7 วันย้อนหลัง (ใช้เปรียบเทียบพัฒนาการต่อเนื่อง ห้ามรายงานซ้ำเรื่องเดิมเว้นแต่มีมิติใหม่):
{history_context}

ข่าวสารรอบ 24 ชม. ที่ตรวจสอบแล้ว:
[ข่าวตลาดไทย & หน่วยงานกำกับ (SET, BOT, สภาพัฒน์, BOI, ก.ล.ต.)]
{thai_news_text}

[ข่าวตลาดโลก & เศรษฐกิจมหภาค (Fed, Wall Street, บอนด์ยีลด์, น้ำมัน, ทองคำ)]
{global_news_text}

ตอบกลับเป็น JSON เท่านั้น (Strict JSON) ตามโครงสร้างที่สมบูรณ์แบบนี้:
{{
  "market_sentiment": {{
    "score": 45,
    "label": "Neutral หรือ Fear หรือ Greed หรือ Extreme Fear หรือ Extreme Greed",
    "rationale": "คำอธิบายสั้นๆ 1 ประโยคว่าทำไมอารมณ์ตลาดวันนี้ถึงเป็นเช่นนี้ (ดูจากบอนด์ยีลด์ ดอลลาร์ และตลาดหุ้น)"
  }},
  "bull_bear": {{
    "bull_pct": 45,
    "bear_pct": 55,
    "summary": "สรุปสั้นๆ 1 ประโยคว่าใครกำลังครองตลาด",
    "bull_drivers": ["ปัจจัยหนุนที่ 1", "ปัจจัยหนุนที่ 2"],
    "bear_drivers": ["ปัจจัยกดดันที่ 1", "ปัจจัยกดดันที่ 2"]
  }},
  "asset_allocation": [
    {{"asset": "เงินสด & ตราสารหนี้ระยะสั้น", "pct": 40, "color": "#06b6d4"}},
    {{"asset": "หุ้นไทยคุณค่า & ปันผลสูง", "pct": 25, "color": "#10b981"}},
    {{"asset": "หุ้นโลก / สินทรัพย์เติบโต", "pct": 25, "color": "#3b82f6"}},
    {{"asset": "ทองคำ & สินทรัพย์ทางเลือก", "pct": 10, "color": "#f59e0b"}}
  ],
  "main_stories": [
    {{
      "threat_level": 5,
      "title": "พาดหัวข่าวสืบสวนที่กระชับ คมชัด ตรงประเด็น",
      "tldr": "สรุปใจความสำคัญแบบหมัดเด็ด 1 ประโยคถ้วนสำหรับคนไม่มีเวลาอ่าน",
      "summary": "เนื้อหาเจาะลึกเชิงโครงสร้าง 2-3 ประโยค",
      "takeaway": "Actionable Takeaway สำหรับพอร์ตลงทุน",
      "continuity": "พัฒนาการต่อเนื่องจากข้อมูลเก่า หรือประเด็นใหม่ล่าสุด",
      "source_name": "ชื่อแหล่งข่าวจากรายการข้างต้น",
      "source_url": "URL ข่าวจริงจากรายการข้างต้น"
    }}
  ],
  "market_briefs": [
    {{
      "tag": "#หมวด เช่น #Macro #Tech #Bonds #FX #Policy",
      "headline": "พาดหัวสั้นกระชับ",
      "text": "เนื้อหาสั้น 1 บรรทัด"
    }}
  ],
  "watchlist": [
    {{
      "time": "ช่วงเวลา เช่น ตลอดวัน หรือ 14:00 น.",
      "event": "วาระเศรษฐกิจที่ต้องจับตาวันนี้"
    }}
  ],
  "beneficiaries": [
    "กลุ่ม/สินทรัพย์ที่ได้ประโยชน์พร้อมเหตุผลสั้นๆ"
  ],
  "risks": [
    "กลุ่ม/สินทรัพย์ที่ต้องระวังพร้อมเหตุผลสั้นๆ"
  ],
  "strategies": [
    "กลยุทธ์จัดพอร์ตเชิงลึก 1 ประโยค"
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
