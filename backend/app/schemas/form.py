from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.form import FormStatus
from app.schemas.question import QuestionOut


class FormBase(BaseModel):
    title: str
    description: Optional[str] = None


class FormCreate(FormBase):
    pass


class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class FormOut(FormBase):
    id: str
    public_id: str
    status: FormStatus
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    question_count: int = 0
    response_count: int = 0

    model_config = {"from_attributes": True}


class FormDetail(FormOut):
    questions: List[QuestionOut] = []

    model_config = {"from_attributes": True}


class FormPublishOut(BaseModel):
    id: str
    public_id: str
    status: FormStatus
    published_at: Optional[datetime]
    public_url: str
