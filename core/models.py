from typing import List, Literal, Optional, Union
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

class PlacementAnswer(BaseModel):
    item_id: str
    choice: Optional[str] = None

class PlacementProduction(BaseModel):
    prompt_id: str
    text: str = ""

class PlacementRequest(BaseModel):
    user_id: str
    answers: List[PlacementAnswer] = []
    production: List[PlacementProduction] = []
    apply_level: bool = False   # finish only: write the placed level into the profile

class PracticeCheckRequest(BaseModel):
    exercise_id: str
    response: Union[str, List[str], None] = None   # text, or the ordered tokens for `order`
    attempt: int = 1

class PracticeResult(BaseModel):
    exercise_id: str
    result: str
    attempts: int = 1

class PracticeFinishRequest(BaseModel):
    user_id: str
    results: List[PracticeResult] = []
