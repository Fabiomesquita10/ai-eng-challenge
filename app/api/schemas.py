from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, description="User message")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    status: Literal["needs_more_info", "completed", "rejected", "error"]
    customer_type: Optional[Literal["regular", "premium", "not_customer"]] = None
    route: Optional[Literal["card", "loan", "insurance", "fraud", "premium", "general"]] = None
    needs_more_info: bool = False


class HealthResponse(BaseModel):
    status: str
