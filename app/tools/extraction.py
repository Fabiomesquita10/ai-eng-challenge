"""Extract intent and identification data from user messages using LLM."""

import json
import re
from typing import Any, Dict, Optional, Tuple

from langchain_openai import ChatOpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

_llm: Optional[ChatOpenAI] = None


def _parse_json_from_llm(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON from LLM response. Handles empty, markdown-wrapped, or malformed output.
    Returns None if parsing fails.
    """
    if not content or not content.strip():
        return None
    text = content.strip()
    # Extract from ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _get_llm() -> ChatOpenAI:
    """ChatOpenAI instance - traced by LangSmith when LANGCHAIN_TRACING_V2=true."""
    global _llm
    if _llm is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        _llm = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.0,
        )
    return _llm


def extract_intent(message: str, conversation_history: Optional[list] = None) -> Tuple[str, float]:
    """
    Extract user intent from message.
    Returns (intent, confidence).
    """
    llm = _get_llm()
    history = conversation_history or []
    context = ""
    if history:
        turns = history[-4:]
        context = "\n".join(
            f"{t.get('role', 'user')}: {t.get('content', '')}" for t in turns
        )
        context = f"Previous conversation:\n{context}\n\n"

    prompt = f"""{context}Current user message: "{message}"

Extract the user's intent. Choose the MOST SPECIFIC match. If they mention a domain (card, loan, insurance, etc.), use that even if they also say "I need help" or "help me".

- card: card issues — lost/stolen/block card, replacement, PIN, cartão, cartao, credit card, debit card
- loan: loan, mortgage, credit application, empréstimo, crédito
- insurance: insurance, policy, yacht, marine, coverage, seguro
- fraud: fraud, suspicious transaction, dispute, unauthorized, fraude
- premium: premium services, private banking, wealth management
- general_support: ONLY when no specific domain is mentioned — vague "I need help", "I have a question", account help, other

Examples: "preciso de ajuda com o meu cartão" → card; "I need help with my card" → card; "help" (no domain) → general_support

Respond with JSON only: {{"intent": "...", "confidence": 0.0-1.0}}"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    data = _parse_json_from_llm(content)
    if data is None:
        return ("general_support", 0.5)
    return (
        data.get("intent", "general_support"),
        float(data.get("confidence", 0.5)),
    )


def extract_identification(
    message: str, conversation_history: Optional[list] = None
) -> Dict[str, Optional[str]]:
    """
    Extract name, phone, IBAN from user message.
    Returns {"name": str|None, "phone": str|None, "iban": str|None}.
    """
    llm = _get_llm()
    history = conversation_history or []
    context = ""
    if history:
        turns = history[-4:]
        context = "\n".join(
            f"{t.get('role', 'user')}: {t.get('content', '')}" for t in turns
        )
        context = f"Previous conversation:\n{context}\n\n"

    prompt = f"""{context}Current user message: "{message}"

Extract identification data from the message. Look for:
- name: full name (e.g. "my name is Fabio Mesquita", "I'm John")
- phone: phone number (with or without country code, spaces, dashes)
- iban: IBAN (starts with country code like PT, DE, GB)

Return JSON only with null for missing fields: {{"name": null, "phone": null, "iban": null}}"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    data = _parse_json_from_llm(content)
    if data is None:
        return {"name": None, "phone": None, "iban": None}
    return {
        "name": data.get("name") if data.get("name") else None,
        "phone": data.get("phone") if data.get("phone") else None,
        "iban": data.get("iban") if data.get("iban") else None,
    }
