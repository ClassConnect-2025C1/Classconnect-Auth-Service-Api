from fastapi import FastAPI
from routes.auth import router as auth_router
from dbConfig.base import Base
from dbConfig.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O podés especificar ["http://192.168.0.14:19006"] si querés restringirlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Servidor FastAPI funcionando 🚀"}
