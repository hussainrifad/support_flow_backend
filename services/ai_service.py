import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:0.6b"
)


def analyze_ticket(title: str, description: str):

    prompt = f"""
You are an AI assistant for a customer support system.

Analyze the following support ticket.

Title:
{title}

Description:
{description}

Return ONLY valid JSON with exactly these fields:

{{
    "category": "string",
    "priority": "LOW",
    "summary": "string",
    "suggested_reply": "string"
}}

IMPORTANT RULES:

1. "category" describes the TYPE of customer problem.
   Examples:
   - Login Problem
   - Account Problem
   - Payment Problem
   - Technical Problem
   - Delivery Problem

2. "priority" describes how urgent the problem is.
   It MUST be exactly one of:
   LOW
   MEDIUM
   HIGH

3. "summary" briefly explains the customer's problem.

4. "suggested_reply" is a polite response that a support agent
   could send to the customer.

Do NOT put LOW, MEDIUM, or HIGH in the category field.

Do NOT include markdown.
Do NOT include ```json.
Do NOT include any explanation outside the JSON.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    result = response.json()

    ai_text = result["response"]

    return json.loads(ai_text)