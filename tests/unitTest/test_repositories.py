import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbConfig.base import Base
from repositories.auth_repository import get_user_by_email, create_user

import uuid

# Configuración de la base de datos en memoria para test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture que crea la DB antes de cada test
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Test de create_user
def test_create_user(db):
    email = "test@example.com"
    password = "securepassword"
    user = create_user(db, email, password)

    assert user.email == email
    assert user.hashed_password != password  # se espera que esté hasheado
    assert isinstance(user.id, uuid.UUID) or isinstance(user.id, str)  # dependiendo de tu tipo de ID

# Test de get_user_by_email
def test_get_user_by_email(db):
    email = "test@example.com"
    password = "securepassword"
    create_user(db, email, password)

    fetched_user = get_user_by_email(db, email)

    assert fetched_user is not None
    assert fetched_user.email == email