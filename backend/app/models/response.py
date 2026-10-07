import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CompletionStatus(str, enum.Enum):
    complete = "complete"
    partial = "partial"


class Response(Base):
    __tablename__ = "responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id = Column(String(36), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completion_status = Column(SAEnum(CompletionStatus), nullable=False, default=CompletionStatus.complete)

    # Relationships
    form = relationship("Form", back_populates="responses")
    answers = relationship(
        "ResponseAnswer",
        back_populates="response",
        cascade="all, delete-orphan",
    )


class ResponseAnswer(Base):
    __tablename__ = "response_answers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id = Column(String(36), ForeignKey("responses.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    # Store answer as text - numbers, ratings, choices all serialized as strings
    answer_value = Column(Text, nullable=True)

    # Relationships
    response = relationship("Response", back_populates="answers")
    question = relationship("Question", back_populates="answers")
