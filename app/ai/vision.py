import google.generativeai as genai
import os
from PIL import Image
import io
import json
import re

API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

def analyze_damage_image(image_bytes: bytes) -> dict:
    if not model:
        return {
            "claim_type": "car",
            "damage_severity": "moderate",
            "estimated_amount": "₹45,000 – ₹72,000",
            "affected_parts": ["front bumper", "hood", "left headlight"],
            "documentation_needed": ["FIR copy", "RC book", "driving license", "repair estimate"],
            "rejection_risks": ["Verify driver had valid license at time of accident"]
        }
    try:
        image = Image.open(io.BytesIO(image_bytes))
        prompt = """
You are an insurance damage assessment expert.
Analyze this damage image and respond ONLY in JSON with these fields:
{
  "claim_type": "car|house|health|business",
  "damage_severity": "minor|moderate|severe|total_loss",
  "estimated_amount": "₹X – ₹Y",
  "affected_parts": ["part1", "part2"],
  "documentation_needed": ["doc1", "doc2"],
  "rejection_risks": ["risk1"]
}
"""
        response = model.generate_content([prompt, image])
        text = response.text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"error": "Could not parse response"}
    except Exception as e:
        return {"error": str(e)}
