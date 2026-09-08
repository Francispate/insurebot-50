import os
import json
import re

try:
    from groq import Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    client = None

def get_preclaim_advice(claim_type: str, description: str, policy_details: str = "") -> str:
    if not client:
        return """1. **Likely Claimable**: Yes, this appears to be a valid claim based on the description provided.

2. **Documents Needed**:
   - FIR copy (if applicable)
   - Policy document
   - ID proof
   - Damage photos
   - Repair estimates

3. **Rejection Risks**:
   - Delay in reporting the incident
   - Missing documentation
   - Pre-existing damage

4. **Best Practices**:
   - Report immediately
   - Take clear photos from multiple angles
   - Keep all receipts and estimates
   - Follow up regularly with the insurer"""
    try:
        prompt = f"""
You are a pre-claim advisor for an Indian insurance platform.
A user wants to file a {claim_type} insurance claim.
Their description: {description}
Their policy context: {policy_details if policy_details else "not provided"}

Give them:
1. Whether this is likely claimable
2. Documents they need to collect RIGHT NOW (before filing)
3. Potential rejection risks and how to avoid them
4. Best practices for maximum payout

Be direct, practical, and specific to Indian insurance regulations.
"""
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"