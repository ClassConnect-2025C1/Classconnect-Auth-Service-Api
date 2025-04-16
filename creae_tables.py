from dbConfig.session import engine
from dbConfig.base import Base  # donde tengas definido Base


Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas correctamente.")