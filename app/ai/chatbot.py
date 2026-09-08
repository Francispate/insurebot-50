import os

try:
    from groq import Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    client = None

SYSTEM_PROMPT = """
You are InsureBot, an intelligent assistant for an Indian insurance platform.
You help users:
- Understand their insurance policies
- Know what is and isn't covered
- Guide them through the claims process
- Answer questions about Indian insurance regulations (IRDAI rules)
- Suggest what documents to keep ready

Be friendly, clear, and practical. Keep answers concise — 3-5 sentences max unless more detail is requested.
If asked about something outside insurance, politely redirect.
"""

def chat(messages: list) -> str:
    if not client:
        return "Hello! I'm InsureBot. I can help you understand your policy, guide you through claims, or answer general insurance questions. What would you like to know?"
    try:
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=full_messages,
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"