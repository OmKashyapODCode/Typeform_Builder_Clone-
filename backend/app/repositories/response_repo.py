from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.response import Response, ResponseAnswer
from app.models.question import Question
from app.schemas.response import ResponseSubmit
import uuid
from datetime import datetime, timezone


class ResponseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_response(self, form_id: str, data: ResponseSubmit) -> Response:
        response = Response(
            id=str(uuid.uuid4()),
            form_id=form_id,
            submitted_at=datetime.now(timezone.utc),
        )
        self.db.add(response)
        self.db.flush()  # Get ID without committing

        for ans in data.answers:
            answer = ResponseAnswer(
                id=str(uuid.uuid4()),
                response_id=response.id,
                question_id=ans.question_id,
                answer_value=ans.answer_value,
            )
            self.db.add(answer)

        self.db.commit()
        self.db.refresh(response)
        return response

    def get_by_form(self, form_id: str) -> List[Response]:
        return (
            self.db.query(Response)
            .filter(Response.form_id == form_id)
            .options(joinedload(Response.answers))
            .order_by(Response.submitted_at.desc())
            .all()
        )

    def get_by_id(self, response_id: str) -> Optional[Response]:
        return (
            self.db.query(Response)
            .filter(Response.id == response_id)
            .options(joinedload(Response.answers).joinedload(ResponseAnswer.question))
            .first()
        )

    def get_answers_for_question(self, question_id: str) -> List[ResponseAnswer]:
        return (
            self.db.query(ResponseAnswer)
            .filter(ResponseAnswer.question_id == question_id)
            .all()
        )
