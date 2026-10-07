import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class FormStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class Form(Base):
    __tablename__ = "forms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="Untitled Form")
    description = Column(Text, nullable=True)
    status = Column(SAEnum(FormStatus), nullable=False, default=FormStatus.draft)
    # Public identifier used in share URLs - stable and separate from internal id
    public_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime, nullable=True)

    # Relationships
    questions = relationship(
        "Question",
        back_populates="form",
        cascade="all, delete-orphan",
        order_by="Question.position",
    )
    responses = relationship(
        "Response",
        back_populates="form",
        cascade="all, delete-orphan",
    )
