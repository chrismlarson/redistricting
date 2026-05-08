from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class Evaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name: str
    state_abbr: str
    chamber: str
    seat_count: int
    notes: str = ""
    report_json: str = ""
    is_seed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
