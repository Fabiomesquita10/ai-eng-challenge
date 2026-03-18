"""Customer verification: 2 out of 3 rule (name, phone, IBAN)."""

from typing import Any, Dict, List, Optional, Tuple

from app.services.customer_service import get_customers


def _normalize_name(value: Optional[str]) -> str:
    if not value:
        return ""
    return value.lower().strip()


def _normalize_phone(value: Optional[str]) -> str:
    if not value:
        return ""
    return "".join(c for c in value if c.isdigit())


def _normalize_iban(value: Optional[str]) -> str:
    if not value:
        return ""
    return value.upper().replace(" ", "").replace("-", "")


def _name_matches(a: Optional[str], b: Optional[str]) -> bool:
    na, nb = _normalize_name(a), _normalize_name(b)
    return bool(na and nb and na == nb)


def _phone_matches(a: Optional[str], b: Optional[str]) -> bool:
    na, nb = _normalize_phone(a), _normalize_phone(b)
    return bool(na and nb and na == nb)


def _iban_matches(a: Optional[str], b: Optional[str]) -> bool:
    na, nb = _normalize_iban(a), _normalize_iban(b)
    return bool(na and nb and na == nb)


def verify_legitimacy(
    collected_data: Dict[str, Optional[str]],
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify customer using 2 out of 3 rule (name, phone, IBAN).
    Returns (is_verified, customer_record or None).
    """
    name = collected_data.get("name")
    phone = collected_data.get("phone")
    iban = collected_data.get("iban")

    # Count non-empty fields
    provided = sum(1 for v in (name, phone, iban) if v and str(v).strip())
    if provided < 2:
        return False, None

    customers = get_customers()
    for customer in customers:
        matches = 0
        if _name_matches(name, customer.get("name")):
            matches += 1
        if _phone_matches(phone, customer.get("phone")):
            matches += 1
        if _iban_matches(iban, customer.get("iban")):
            matches += 1
        if matches >= 2:
            record = {
                "name": customer.get("name"),
                "phone": customer.get("phone"),
                "iban": customer.get("iban"),
                "premium": customer.get("premium", False),
                "secret": customer.get("secret"),
                "answer": customer.get("answer"),
            }
            return True, record

    return False, None
