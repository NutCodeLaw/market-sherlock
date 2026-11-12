"""
AI Investigator Module - Gemini-powered financial intelligence & portfolio analysis
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

    prompt = f"""คุณคือหัวหน้านักสืบและหัวหน้านักกลยุทธ์การลงทุนอาวุโสแห่ง 'MarketSherlock'
ภารกิจของคุณคือ: ผลิตรายงาน 'สรุปข่าวเศรษฐกิจทั่วโลก (8.00 น.)' ประจำวันที่ {thai_date}

ข้อมูลตัวเลขตลาดล่าสุด (Market Snapshot):
{market_snapshot_text}

ประวัติข่าวเด่นที่รายงานไปแล้วในช่วง 7 วันที่ผ่านมา (ใช้สำหรับตรวจสอบความคืบหน้าและห้ามรายงานซ้ำเรื่องเดิม เว้นแต่มีพัฒนาการใหม่ที่มีนัยสำคัญ):
{history_context}

ข่าวสารสดใหม่ในรอบ 24 ชั่วโมงที่รวบรวมจากแหล่งข่าวที่เชื่อถือได้:
[ข่าวตลาดไทย & หน่วยงานกำกับ (SET, BOT, สภาพัฒน์, BOI, ก.ล.ต.)]
{thai_news_text}

[ข่าวตลาดโลก & เศรษฐกิจมหภาค (Fed, Wall Street, พันธบัตร, น้ำมัน, ทองคำ)]
{global_news_text}

กติกาและมาตรฐานการสืบสวนของ MarketSherlock:
1. คัดเลือกเฉพาะ 3-5 ข่าวเด่นที่มีนัยสำคัญเชิงโครงสร้าง (Investigative & Structural Impact) ทั้งตลาดไทยและตลาดโลก โดยกรองข่าวลือ ข่าวสแปม หรือข่าวไร้สาระออกทั้งหมด
2. เชื่อมโยงกับประวัติข่าวย้อนหลัง: หากเป็นประเด็นต่อเนื่อง ให้ชี้ชัดถึง 'พัฒนาการล่าสุดวันนี้' (หลีกเลี่ยงการเล่าเรื่องเก่าซ้ำ) หากเป็นเรื่องใหม่ ให้ระบุชัดเจน
3. วิเคราะห์เจาะลึกนัยเชิงกลยุทธ์ต่อพอร์ตการลงทุนอย่างเป็นรูปธรรม: กลุ่มใดได้ประโยชน์ (Beneficiaries), กลุ่มใดต้องระวัง (Risks), และ Actionable Takeaway
4. เขียนด้วยภาษาที่กระชับ คมคาย สดใหม่ อ่านสนุก ไม่น่าเบื่อ ชวนติดตามทุกเช้า
5. นำ URL ลิงก์ข่าวจริงจากรายการด้านบนมาแนบในแต่ละข่าว ห้ามมโนลิงก์ขึ้นมาเองเด็ดขาด

ตอบกลับเป็น JSON เท่านั้น (Strict JSON) ตามโครงสร้างนี้:
{{
  "main_stories": [
    {{
      "title": "พาดหัวข่าวเชิงสืบสวนที่คมชัด",
      "summary": "เนื้อหาข่าวสรุปเจาะลึก 3-4 ประโยค พร้อมบริบทเชิงโครงสร้าง",
      "takeaway": "Actionable Takeaway สำหรับนักลงทุน",
      "continuity": "ความคืบหน้าจากสัปดาห์ก่อน หรือ ประเด็นใหม่ที่ต้องจับตา",
      "source_name": "ชื่อแหล่งข่าวที่ปรากฏในรายการ",
      "source_url": "URL ข่าวจริงจากรายการ"
    }}
  ],
  "market_briefs": [
    {{
      "tag": "#หมวดหมู่ เช่น #Macro #Tech #Energy #Policy",
      "headline": "พาดหัวข่าวสั้น",
      "text": "สรุปสั้น 1-2 ประโยค"
    }}
  ],
  "watchlist": [
    {{
      "time": "ช่วงเวลา เช่น 14:00 น. หรือ ตลอดวัน",
      "event": "วาระเศรษฐกิจหรือเหตุการณ์ที่ต้องจับตาวันนี้"
    }}
  ],
  "beneficiaries": [
    "กลุ่มหรือหุ้นที่ได้ประโยชน์พร้อมเหตุผลสั้นๆ"
  ],
  "risks": [
    "กลุ่มหรือสินทรัพย์ที่ต้องระวังพร้อมเหตุผลสั้นๆ"
  ],
  "strategies": [
    "คำแนะนำการจัดสรรพอร์ตหรือกลยุทธ์การลงทุนเชิงลึก"
  ]
}}
"""
    return prompt

def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Clean markdown formatting and extract JSON object."""
    # Strip markdown code blocks
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    
    # Try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback regex search for { ... }
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
