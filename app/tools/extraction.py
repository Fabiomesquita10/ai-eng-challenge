"""Extract intent and identification data from user messages using LLM."""

import json
from typing import Dict, Optional, Tuple

from langchain_openai import ChatOpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

_llm: Optional[ChatOpenAI] = None


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

Extract the user's intent. Choose one:
- card: lost card, stolen card, block card, replacement, PIN
- loan: loan, mortgage, credit application
- insurance: insurance, policy, yacht, marine, coverage
- fraud: fraud, suspicious transaction, dispute, unauthorized
- premium: premium services, private banking, wealth management
- general_support: general inquiry, account help, other

Respond with JSON only: {{"intent": "...", "confidence": 0.0-1.0}}"""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    data = json.loads(content)
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
    data = json.loads(content)
    return {
        "name": data.get("name") if data.get("name") else None,
        "phone": data.get("phone") if data.get("phone") else None,
        "iban": data.get("iban") if data.get("iban") else None,
    }
