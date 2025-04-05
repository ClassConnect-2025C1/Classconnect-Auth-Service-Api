from fastapi import FastAPI
from routes.auth import router as auth_router
from dbConfig.base import Base
from dbConfig.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Servidor FastAPI funcionando 🚀"}
