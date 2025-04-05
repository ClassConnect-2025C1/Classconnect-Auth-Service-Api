import pytest
from sqlalchemy.exc import OperationalError
from dbConfig import postgres
import os
from dotenv import load_dotenv
load_dotenv()
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_database_connection():
    try:
        
        with postgres.engine.connect() as conn:
            assert conn.closed == False
    except OperationalError as e:
        pytest.fail(f"Not able to connect to the database: {e}")

