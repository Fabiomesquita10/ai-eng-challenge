"""Application configuration from environment variables."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)


# OpenAI
OPENAI_API_KEY: Optional[str] = _get("OPENAI_API_KEY")
OPENAI_MODEL: str = _get("OPENAI_MODEL") or "gpt-4o-mini"
