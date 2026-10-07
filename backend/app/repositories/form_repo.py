from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.form import Form, FormStatus
from app.models.question import Question
from app.models.response import Response
from app.schemas.form import FormCreate, FormUpdate
from datetime import datetime, timezone
import uuid


class FormRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Form]:
        forms = self.db.query(Form).order_by(Form.created_at.desc()).all()
        return forms

    def get_by_id(self, form_id: str) -> Optional[Form]:
        return self.db.query(Form).filter(Form.id == form_id).first()

    def get_by_public_id(self, public_id: str) -> Optional[Form]:
        return self.db.query(Form).filter(Form.public_id == public_id).first()

    def create(self, data: FormCreate) -> Form:
        form = Form(
            id=str(uuid.uuid4()),
            public_id=str(uuid.uuid4()),
            title=data.title,
            description=data.description,
        )
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def update(self, form: Form, data: FormUpdate) -> Form:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(form, key, value)
        form.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(form)
        return form

    def publish(self, form: Form) -> Form:
        form.status = FormStatus.published
        form.published_at = datetime.now(timezone.utc)
        form.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(form)
        return form

    def unpublish(self, form: Form) -> Form:
        form.status = FormStatus.draft
        form.published_at = None
        form.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(form)
        return form

    def delete(self, form: Form) -> None:
        self.db.delete(form)
        self.db.commit()

    def duplicate(self, form: Form) -> Form:
        """Create a copy of the form with all questions but no responses."""
        new_form = Form(
            id=str(uuid.uuid4()),
            public_id=str(uuid.uuid4()),
            title=f"{form.title} (Copy)",
            description=form.description,
            status=FormStatus.draft,
        )
        self.db.add(new_form)
        self.db.flush()

        # Copy questions preserving order
        for q in form.questions:
            new_q = Question(
                id=str(uuid.uuid4()),
                form_id=new_form.id,
                type=q.type,
                title=q.title,
                description=q.description,
                position=q.position,
                required=q.required,
                settings=q.settings,
            )
            self.db.add(new_q)

        self.db.commit()
        self.db.refresh(new_form)
        return new_form

    def get_response_count(self, form_id: str) -> int:
        return self.db.query(func.count(Response.id)).filter(Response.form_id == form_id).scalar() or 0

    def get_question_count(self, form_id: str) -> int:
        return self.db.query(func.count(Question.id)).filter(Question.form_id == form_id).scalar() or 0
