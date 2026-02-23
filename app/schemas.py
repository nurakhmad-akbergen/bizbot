from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any

Intent = Literal["sale", "expense", "stock_in", "adjust", "report_request", "unknown"]

class ParsedMessage(BaseModel):
    intent: Intent
    occurred_at: Optional[str] = Field(default=None, description="ISO 8601 datetime if extracted, else null")
    item_name: Optional[str] = None
    qty: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    currency: Literal["KZT"] = "KZT"
    note: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    need_clarification: bool = False
    clarification_question: Optional[str] = None

class ReportRequest(BaseModel):
    kind: Literal["today", "date", "range"] = "today"
    date: Optional[str] = None          # YYYY-MM-DD
    start_date: Optional[str] = None    # YYYY-MM-DD
    end_date: Optional[str] = None      # YYYY-MM-DD