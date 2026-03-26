from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic
import os

router = APIRouter(prefix="/api", tags=["scan"])
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class EmailScanRequest(BaseModel):
    email_content: str
    sender: str = ""
    subject: str = ""


class ThreatResult(BaseModel):
    risk_score: int          # 0–100
    risk_level: str          # LOW / MEDIUM / HIGH / CRITICAL
    is_phishing: bool
    indicators: list[str]    # plain-English red flags found
    recommendation: str      # what the user should do


@router.post("/scan/email", response_model=ThreatResult)
async def scan_email(request: EmailScanRequest):
    if not request.email_content.strip():
        raise HTTPException(status_code=400, detail="Email content cannot be empty.")

    prompt = f"""You are an expert cybersecurity analyst specializing in phishing detection.

Analyze the following email for phishing indicators and return a JSON response ONLY (no extra text).

Email details:
- Sender: {request.sender or 'Unknown'}
- Subject: {request.subject or 'Unknown'}
- Body:
{request.email_content}

Return this exact JSON structure:
{{
  "risk_score": <integer 0-100>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "is_phishing": <true|false>,
  "indicators": ["<plain English red flag 1>", "<red flag 2>", ...],
  "recommendation": "<one clear sentence telling the user what to do>"
}}

Risk score guide:
- 0-25: LOW (likely legitimate)
- 26-50: MEDIUM (suspicious, verify before acting)
- 51-75: HIGH (likely phishing, do not click links)
- 76-100: CRITICAL (confirmed phishing, report immediately)"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        result = json.loads(message.content[0].text)
        return ThreatResult(**result)
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"AI response parsing failed: {str(e)}")
