from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.form_service import FormService
from app.services.response_service import ResponseService
from app.schemas.form import FormDetail
from app.schemas.response import ResponseSubmit, ResponseOut

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/forms/{public_id}", response_model=FormDetail)
def get_public_form(public_id: str, db: Session = Depends(get_db)):
    """
    Public endpoint - get a published form by its public ID.
    Returns 404 if form not found, 403 if form is draft.
    """
    from fastapi import HTTPException
    from app.repositories.form_repo import FormRepository
    from app.models.form import FormStatus

    form_repo = FormRepository(db)
    form = form_repo.get_by_public_id(public_id)

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if form.status != FormStatus.published:
        raise HTTPException(status_code=403, detail="This form is not currently accepting responses")

    form_detail = FormDetail.model_validate(form)
    form_detail.question_count = len(form.questions)
    form_detail.response_count = form_repo.get_response_count(form.id)
    return form_detail


@router.post("/forms/{public_id}/responses", response_model=ResponseOut, status_code=201)
def submit_response(public_id: str, data: ResponseSubmit, db: Session = Depends(get_db)):
    """Submit a response to a published form."""
    return ResponseService(db).submit_response(public_id, data)
