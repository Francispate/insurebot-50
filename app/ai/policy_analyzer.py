import fitz
import os
import json
import re

try:
    from groq import Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    client = None

def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text[:8000]
    except Exception as e:
        return ""

def analyze_policy_text(text: str) -> dict:
    if not client:
        return {
            "policy_summary": "Comprehensive motor insurance policy",
            "what_is_covered": ["accident damage", "theft", "fire", "natural calamity"],
            "what_is_NOT_covered": ["drunk driving", "war", "nuclear risk"],
            "hidden_benefits": ["Free roadside assistance", "No-claim bonus up to 50%"],
            "dangerous_clauses": ["Must report within 24 hours of incident"],
            "overall_rating": 7.5
        }
    try:
        prompt = f"""
You are an insurance policy expert. Analyze this policy document and respond ONLY in JSON:
{{
  "policy_summary": "2-3 sentence summary",
  "what_is_covered": ["item1", "item2"],
  "what_is_NOT_covered": ["item1", "item2"],
  "hidden_benefits": ["benefit1"],
  "dangerous_clauses": ["clause1"],
  "overall_rating": 7.5
}}

Policy text:
{text}
"""
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        text_resp = response.choices[0].message.content
        match = re.search(r'\{.*\}', text_resp, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Could not parse"}
    except Exception as e:
        return {"error": str(e)}