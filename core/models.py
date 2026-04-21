from typing import List, Literal, Optional
from pydantic import BaseModel

class UserSettings(BaseModel):
    user_id: str
    target_language: str = "en"
    native_language: str = "ru"
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = "A1"
    interests: List[str] = []

class ChatRequest(BaseModel):
    user_id: str
    message: str

class LessonStartRequest(BaseModel):
    user_id: str
    scenario_id: str

class LessonMessageRequest(BaseModel):
    user_id: str
    message: str
