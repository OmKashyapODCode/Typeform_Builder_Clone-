from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.question import Question, QuestionType
from app.schemas.question import QuestionCreate, QuestionUpdate
from datetime import datetime, timezone
import uuid


# Default question titles by type
DEFAULT_TITLES = {
    QuestionType.short_text: "What is your name?",
    QuestionType.long_text: "Tell us a little about yourself.",
    QuestionType.multiple_choice: "Which option best describes you?",
    QuestionType.dropdown: "Select your department",
    QuestionType.email: "What is your email address?",
    QuestionType.number: "How many years of experience do you have?",
    QuestionType.yes_no: "Would you recommend us?",
    QuestionType.rating: "How would you rate your experience?",
}

DEFAULT_SETTINGS = {
    QuestionType.multiple_choice: {"choices": ["Option A", "Option B", "Option C"], "allow_other": False},
    QuestionType.dropdown: {"choices": ["Engineering", "Design", "Marketing", "Sales", "Operations"]},
    QuestionType.rating: {"max_rating": 5},
    QuestionType.number: {"min_value": None, "max_value": None},
}


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: str) -> Optional[Question]:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def get_by_form(self, form_id: str) -> List[Question]:
        return (
            self.db.query(Question)
            .filter(Question.form_id == form_id)
            .order_by(Question.position)
            .all()
        )

    def get_max_position(self, form_id: str) -> int:
        from sqlalchemy import func
        result = self.db.query(func.max(Question.position)).filter(Question.form_id == form_id).scalar()
        return result if result is not None else -1

    def create(self, form_id: str, data: QuestionCreate) -> Question:
        max_pos = self.get_max_position(form_id)
        # Apply defaults for title if not provided or empty
        title = data.title or DEFAULT_TITLES.get(data.type, "Untitled Question")
        # Merge default settings with provided settings
        default_settings = DEFAULT_SETTINGS.get(data.type, {}).copy()
        if data.settings:
            default_settings.update(data.settings)

        question = Question(
            id=str(uuid.uuid4()),
            form_id=form_id,
            type=data.type,
            title=title,
            description=data.description,
            position=max_pos + 1,
            required=data.required,
            settings=default_settings,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, question: Question, data: QuestionUpdate) -> Question:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(question, key, value)
        question.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question: Question) -> None:
        form_id = question.form_id
        position = question.position
        self.db.delete(question)
        # Reindex remaining questions
        remaining = (
            self.db.query(Question)
            .filter(Question.form_id == form_id, Question.position > position)
            .order_by(Question.position)
            .all()
        )
        for q in remaining:
            q.position -= 1
        self.db.commit()

    def reorder(self, form_id: str, question_ids: List[str]) -> List[Question]:
        """Reorder questions by assigning new positions based on the provided order."""
        questions_map = {
            q.id: q for q in self.get_by_form(form_id)
        }
        for idx, qid in enumerate(question_ids):
            if qid in questions_map:
                questions_map[qid].position = idx
        self.db.commit()
        return self.get_by_form(form_id)
