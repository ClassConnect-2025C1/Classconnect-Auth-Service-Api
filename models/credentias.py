from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from app.db.base import Base  # definimos Base desde SQLAlchemy


class credentiasl(Base):
    __tablename__ = "credentias"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

