# schemas/pydantic_schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- User schemas ---
class UserCreate(BaseModel):
    name: str
    target_score: float
    onboarding_summary: Optional[str] = None

class UserRead(BaseModel):
    id: int
    name: str
    target_score: float
    current_week: int
    onboarding_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Session schemas ---
class SessionCreate(BaseModel):
    user_id: int
    week_number: int
    scenario_type: Optional[str] = "job interview"

class SessionUpdate(BaseModel):
    score: float
    feedback_summary: str

class SessionRead(BaseModel):
    id: int
    user_id: int
    week_number: int
    score: Optional[float]
    scenario_type: Optional[str]
    feedback_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- BehavioralFlag schemas ---
class FlagCreate(BaseModel):
    user_id: int
    flag_text: str
    week_identified: int

class FlagRead(BaseModel):
    id: int
    user_id: int
    flag_text: str
    week_identified: int

    class Config:
        from_attributes = True

# --- Context schema (output of context aggregator) ---
class CoachingContext(BaseModel):
    user_name: str
    current_week: int
    target_score: float
    average_score: Optional[float]
    score_delta: Optional[float]           # latest score minus previous score
    behavioral_flags: List[str]
    past_feedback_summaries: List[str]     # from ChromaDB
    onboarding_summary: Optional[str]
    progress_narrative: str                # human-readable summary string for prompt injection
