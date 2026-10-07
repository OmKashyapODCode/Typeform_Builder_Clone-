from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.form_service import FormService
from app.schemas.form import FormCreate, FormUpdate, FormOut, FormDetail, FormPublishOut

router = APIRouter(prefix="/api/forms", tags=["forms"])


@router.get("", response_model=List[FormOut])
def list_forms(db: Session = Depends(get_db)):
    """List all forms for the creator dashboard."""
    return FormService(db).list_forms()


@router.post("", response_model=FormDetail, status_code=201)
def create_form(data: FormCreate, db: Session = Depends(get_db)):
    """Create a new form."""
    return FormService(db).create_form(data)


@router.get("/{form_id}", response_model=FormDetail)
def get_form(form_id: str, db: Session = Depends(get_db)):
    """Get a form with all questions."""
    return FormService(db).get_form(form_id)


@router.patch("/{form_id}", response_model=FormDetail)
def update_form(form_id: str, data: FormUpdate, db: Session = Depends(get_db)):
    """Update form metadata (title, description)."""
    return FormService(db).update_form(form_id, data)


@router.delete("/{form_id}", status_code=204)
def delete_form(form_id: str, db: Session = Depends(get_db)):
    """Delete a form and all its questions/responses."""
    FormService(db).delete_form(form_id)


@router.post("/{form_id}/publish", response_model=FormPublishOut)
def publish_form(form_id: str, db: Session = Depends(get_db)):
    """Publish the form - makes it publicly accessible."""
    return FormService(db).publish_form(form_id)


@router.post("/{form_id}/unpublish", response_model=FormPublishOut)
def unpublish_form(form_id: str, db: Session = Depends(get_db)):
    """Unpublish the form - removes public access."""
    return FormService(db).unpublish_form(form_id)


@router.post("/{form_id}/duplicate", response_model=FormDetail, status_code=201)
def duplicate_form(form_id: str, db: Session = Depends(get_db)):
    """Duplicate a form without copying responses."""
    return FormService(db).duplicate_form(form_id)
