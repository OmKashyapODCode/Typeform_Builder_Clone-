from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.question_service import QuestionService
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionOut, QuestionReorder

router = APIRouter(tags=["questions"])


@router.post("/api/forms/{form_id}/questions", response_model=QuestionOut, status_code=201)
def add_question(form_id: str, data: QuestionCreate, db: Session = Depends(get_db)):
    """Add a new question to a form."""
    return QuestionService(db).add_question(form_id, data)


@router.patch("/api/forms/{form_id}/questions/reorder", response_model=List[QuestionOut])
def reorder_questions(form_id: str, data: QuestionReorder, db: Session = Depends(get_db)):
    """Reorder questions by providing the ordered list of question IDs."""
    return QuestionService(db).reorder_questions(form_id, data)


@router.patch("/api/questions/{question_id}", response_model=QuestionOut)
def update_question(question_id: str, data: QuestionUpdate, db: Session = Depends(get_db)):
    """Update a specific question."""
    return QuestionService(db).update_question(question_id, data)


@router.delete("/api/questions/{question_id}", status_code=204)
def delete_question(question_id: str, db: Session = Depends(get_db)):
    """Delete a specific question."""
    QuestionService(db).delete_question(question_id)
