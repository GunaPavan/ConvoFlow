# src/api/main.py
from dotenv import load_dotenv
load_dotenv()  # must be first

from fastapi import FastAPI
from src.api.routes.respond import router as respond_router

app = FastAPI()
app.include_router(respond_router)
