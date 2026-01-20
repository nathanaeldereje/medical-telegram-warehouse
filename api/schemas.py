# api\schemas.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

# --- Schemas for Channel Activity ---
class ChannelActivity(BaseModel):
    date: date
    channel_name: str
    post_count: int

# --- Schemas for Top Products/Terms ---
class TrendingTerm(BaseModel):
    term: str
    count: int

# --- Schemas for Message Search ---
class MessageResponse(BaseModel):
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: Optional[str]
    view_count: int
    
    class Config:
        from_attributes = True

# --- Schemas for Visual Stats ---
class VisualStat(BaseModel):
    image_category: str
    count: int
    avg_confidence: float