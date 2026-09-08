import requests
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

def search_insurance_info(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Tavily API key not configured. Please add TAVILY_API_KEY to your .env file."
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": f"India insurance {query}",
                "search_depth": "advanced",
                "max_results": 5,
                "include_answer": True
            },
            timeout=30
        )
        data = response.json()
        answer = data.get("answer", "")
        sources = [r["content"] for r in data.get("results", [])[:3]]
        combined = answer + "\n\n" + "\n\n".join(sources)
        return combined[:3000]
    except Exception as e:
        return f"Search error: {str(e)}"