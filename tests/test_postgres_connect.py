import pytest
from dbConfig.postgres import connect_to_db  # Asegúrate de que el import sea correcto
from dbConfig.postgres import create_database  # Asegúrate de que el import sea correcto
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



