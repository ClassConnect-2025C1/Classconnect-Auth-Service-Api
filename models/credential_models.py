import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    failed_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    is_locked = Column(Boolean, default=False)
    lock_until = Column(DateTime, nullable=True)


