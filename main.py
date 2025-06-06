from fastapi import FastAPI
from routes.auth import router as auth_router
from dbConfig.base import Base
from dbConfig.session import engine
from middleware.datadog_logger import setup_datadog_logging
import os
from dotenv import load_dotenv

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
# Setup Datadog logging
load_dotenv()
datadog_api_key = os.getenv("DATADOG_API_KEY")
dd_logger = setup_datadog_logging(app, datadog_api_key)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Servidor FastAPI funcionando 🚀"}
