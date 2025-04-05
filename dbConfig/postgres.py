from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Database connection URL
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create a new SQLAlchemy engine instance

engine = create_engine(DATABASE_URL)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a new session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
