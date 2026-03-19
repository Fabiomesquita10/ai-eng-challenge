"""Build greeter responses for different scenarios."""

from typing import Dict, List, Optional


def merge_collected_data(
    existing: Dict[str, Optional[str]], new: Dict[str, Optional[str]]
) -> Dict[str, Optional[str]]:
    """Merge new data into existing. New values override only if non-empty."""
    result = dict(existing)
    for key, value in new.items():
        if value and str(value).strip():
            result[key] = value.strip()
    return result


def compute_missing_fields(collected_data: Dict[str, Optional[str]]) -> List[str]:
    """Return list of empty fields: name, phone, iban."""
    missing = []
    for field in ("name", "phone", "iban"):
        val = collected_data.get(field)
        if not val or not str(val).strip():
            missing.append(field)
    return missing


def has_minimum_identification_data(collected_data: Dict[str, Optional[str]]) -> bool:
    """True if at least 2 of 3 fields are present."""
    filled = sum(
        1 for f in ("name", "phone", "iban") if collected_data.get(f) and str(collected_data.get(f)).strip()
    )
    return filled >= 2


def build_followup_response(
    collected_data: Dict[str, Optional[str]],
    missing_fields: List[str],
) -> str:
    """Build message when more identification is needed."""
    name = collected_data.get("name")
    greeting = f"Thanks, {name}." if name else "Thanks for reaching out."
    if "phone" in missing_fields and "iban" in missing_fields:
        return f"{greeting} To verify your identity, could you please provide your phone number or IBAN?"
    if "phone" in missing_fields:
        return f"{greeting} To verify your identity, could you please provide your phone number?"
    if "iban" in missing_fields:
        return f"{greeting} To verify your identity, could you please provide your IBAN?"
    return f"{greeting} To verify your identity, could you please provide your phone number or IBAN?"


def build_identification_failure_response() -> str:
    """Build message when verification fails."""
    return (
        "I'm sorry, I couldn't verify your details with the information provided. "
        "If you're a new customer, I can guide you to our onboarding team."
    )


def build_identified_response(name: Optional[str]) -> str:
    """Build short confirmation when identified."""
    if name:
        return f"Thanks, {name}. I've verified your identity."
    return "Thanks. I've verified your identity."


def build_secret_question_response(secret_question: str) -> str:
    """Build message asking the customer's secret question."""
    return f"For security, please answer: {secret_question}"
