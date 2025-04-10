from sqlalchemy import Column,String
from dbConfig.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID 

class Credential(Base):
    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

