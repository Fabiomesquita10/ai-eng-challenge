"""Customer data service."""

import json
from pathlib import Path
from typing import Any, List, Optional

CUSTOMERS_PATH = Path(__file__).resolve().parent.parent / "data" / "customers.json"

_customers_cache: Optional[List[dict]] = None


def get_customers() -> List[dict[str, Any]]:
    """Load customers from JSON. Cached after first load."""
    global _customers_cache
    if _customers_cache is not None:
        return _customers_cache
    with open(CUSTOMERS_PATH, encoding="utf-8") as f:
        _customers_cache = json.load(f)
    return _customers_cache
