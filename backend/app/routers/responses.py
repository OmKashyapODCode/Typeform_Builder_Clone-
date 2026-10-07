from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.response_service import ResponseService
from app.schemas.response import ResponseOut, ResponseSummary, FormAnalytics

router = APIRouter(prefix="/api", tags=["responses"])


@router.get("/forms/{form_id}/responses", response_model=List[ResponseSummary])
def get_responses(form_id: str, db: Session = Depends(get_db)):
    """Get all responses for a form."""
    return ResponseService(db).get_responses(form_id)


@router.get("/responses/{response_id}", response_model=ResponseOut)
def get_response(response_id: str, db: Session = Depends(get_db)):
    """Get a single response with all answers."""
    return ResponseService(db).get_response(response_id)


@router.get("/forms/{form_id}/analytics", response_model=FormAnalytics)
def get_analytics(form_id: str, db: Session = Depends(get_db)):
    """Get analytics for a form."""
    return ResponseService(db).get_analytics(form_id)
