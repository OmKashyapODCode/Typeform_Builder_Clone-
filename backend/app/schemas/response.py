from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnswerSubmit(BaseModel):
    question_id: str
    answer_value: Optional[str] = None


class ResponseSubmit(BaseModel):
    answers: List[AnswerSubmit]


class ResponseAnswerOut(BaseModel):
    id: str
    question_id: str
    answer_value: Optional[str]
    question_title: Optional[str] = None
    question_type: Optional[str] = None

    model_config = {"from_attributes": True}


class ResponseOut(BaseModel):
    id: str
    form_id: str
    submitted_at: datetime
    completion_status: str
    answers: List[ResponseAnswerOut] = []

    model_config = {"from_attributes": True}


class ResponseSummary(BaseModel):
    id: str
    form_id: str
    submitted_at: datetime
    completion_status: str
    answer_count: int = 0

    model_config = {"from_attributes": True}


# Analytics schemas
class ChoiceDistribution(BaseModel):
    option: str
    count: int
    percentage: float


class QuestionAnalytics(BaseModel):
    question_id: str
    question_title: str
    question_type: str
    total_answers: int
    # Type-specific stats
    distribution: Optional[List[ChoiceDistribution]] = None  # multiple_choice, dropdown, yes_no
    average: Optional[float] = None           # rating, number
    min_value: Optional[float] = None         # number, rating
    max_value: Optional[float] = None         # number, rating
    rating_distribution: Optional[Dict[str, int]] = None   # rating only


class FormAnalytics(BaseModel):
    form_id: str
    total_responses: int
    questions: List[QuestionAnalytics]
