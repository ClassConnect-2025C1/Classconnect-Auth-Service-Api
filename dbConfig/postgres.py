import psycopg2

import psycopg2
import os

# This credential need to put in envioroment variable
DB_USER = "postgres"
DB_PASSWORD = 1234
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "test_db"

def create_database():
    """Crea la base de datos si no existe."""
    try:
       
        conn = psycopg2.connect(
            dbname="postgres",  
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

      
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        exists = cur.fetchone()

      
        if not exists:
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"✅ Base de datos '{DB_NAME}' creada.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ No se pudo crear la base de datos: {e}")

def connect_to_db():
    """Intenta conectarse a la base de datos."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None