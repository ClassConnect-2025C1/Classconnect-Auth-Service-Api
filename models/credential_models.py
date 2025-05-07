from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime, timezone

from dbConfig.base import Base  

 
 
class Credential(Base):
     __tablename__ = "credentials"
 
     id = Column(UUID(as_uuid=True), primary_key=True)
     email = Column(String, unique=True, index=True, nullable=False)
     hashed_password = Column(String, nullable=True)
     failed_attempts = Column(Integer, default=0)
     last_failed_login = Column(DateTime, nullable=True)
     is_locked = Column(Boolean, default=False)
     lock_until = Column(DateTime, nullable=True)
     is_verified = Column(Boolean, default=False)       


class VerificationPin(Base):
    __tablename__ = "verification_pins"

    email = Column(String, unique=True, nullable=False, primary_key=True)
    pin = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    is_valid = Column(Boolean, default=True)

class RecoveryLink(Base):
     __tablename__ = "recovery_links"
     
     id = Column(UUID(as_uuid=True), primary_key=True)
     user_id = Column(UUID(as_uuid=True), nullable=False)
     recovery_link = Column(UUID(as_uuid=True), nullable=False)
     created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))