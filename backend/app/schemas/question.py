from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.models.question import QuestionType


class QuestionSettings(BaseModel):
    """Type-specific settings stored as JSON."""
    choices: Optional[List[str]] = None        # multiple_choice / dropdown
    allow_other: Optional[bool] = False        # multiple_choice
    max_rating: Optional[int] = 5             # rating
    placeholder: Optional[str] = None         # text inputs
    min_value: Optional[float] = None         # number
    max_value: Optional[float] = None         # number


class QuestionBase(BaseModel):
    type: QuestionType
    title: str
    description: Optional[str] = None
    required: bool = False
    settings: Optional[Dict[str, Any]] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    type: Optional[QuestionType] = None


class QuestionOut(QuestionBase):
    id: str
    form_id: str
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionReorder(BaseModel):
    """List of question IDs in the desired order."""
    question_ids: List[str]
