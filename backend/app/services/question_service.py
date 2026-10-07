from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.repositories.question_repo import QuestionRepository
from app.repositories.form_repo import FormRepository
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionOut, QuestionReorder


class QuestionService:
    def __init__(self, db: Session):
        self.q_repo = QuestionRepository(db)
        self.f_repo = FormRepository(db)

    def _get_form_or_404(self, form_id: str):
        form = self.f_repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        return form

    def _get_question_or_404(self, question_id: str):
        q = self.q_repo.get_by_id(question_id)
        if not q:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        return q

    def add_question(self, form_id: str, data: QuestionCreate) -> QuestionOut:
        self._get_form_or_404(form_id)
        question = self.q_repo.create(form_id, data)
        return QuestionOut.model_validate(question)

    def update_question(self, question_id: str, data: QuestionUpdate) -> QuestionOut:
        q = self._get_question_or_404(question_id)
        q = self.q_repo.update(q, data)
        return QuestionOut.model_validate(q)

    def delete_question(self, question_id: str) -> None:
        q = self._get_question_or_404(question_id)
        self.q_repo.delete(q)

    def reorder_questions(self, form_id: str, data: QuestionReorder) -> List[QuestionOut]:
        self._get_form_or_404(form_id)
        questions = self.q_repo.reorder(form_id, data.question_ids)
        return [QuestionOut.model_validate(q) for q in questions]
