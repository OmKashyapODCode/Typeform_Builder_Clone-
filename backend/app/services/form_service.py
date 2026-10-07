from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.repositories.form_repo import FormRepository
from app.schemas.form import FormCreate, FormUpdate, FormOut, FormDetail, FormPublishOut
from app.schemas.question import QuestionOut


class FormService:
    def __init__(self, db: Session):
        self.repo = FormRepository(db)

    def list_forms(self) -> List[FormOut]:
        forms = self.repo.get_all()
        result = []
        for form in forms:
            form_out = FormOut.model_validate(form)
            form_out.question_count = self.repo.get_question_count(form.id)
            form_out.response_count = self.repo.get_response_count(form.id)
            result.append(form_out)
        return result

    def create_form(self, data: FormCreate) -> FormDetail:
        form = self.repo.create(data)
        form_detail = FormDetail.model_validate(form)
        form_detail.questions = []
        form_detail.question_count = 0
        form_detail.response_count = 0
        return form_detail

    def get_form(self, form_id: str) -> FormDetail:
        form = self.repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        form_detail = FormDetail.model_validate(form)
        form_detail.question_count = len(form.questions)
        form_detail.response_count = self.repo.get_response_count(form.id)
        return form_detail

    def update_form(self, form_id: str, data: FormUpdate) -> FormDetail:
        form = self.repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        form = self.repo.update(form, data)
        return self.get_form(form_id)

    def delete_form(self, form_id: str) -> None:
        form = self.repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        self.repo.delete(form)

    def publish_form(self, form_id: str) -> FormPublishOut:
        form = self.repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        form = self.repo.publish(form)
        return FormPublishOut(
            id=form.id,
            public_id=form.public_id,
            status=form.status,
            published_at=form.published_at,
            public_url=f"/form/{form.public_id}",
        )

    def unpublish_form(self, form_id: str) -> FormPublishOut:
        form = self.repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        form = self.repo.unpublish(form)
        return FormPublishOut(
            id=form.id,
            public_id=form.public_id,
            status=form.status,
            published_at=form.published_at,
            public_url=f"/form/{form.public_id}",
        )

    def duplicate_form(self, form_id: str) -> FormDetail:
        form = self.repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        new_form = self.repo.duplicate(form)
        return self.get_form(new_form.id)
