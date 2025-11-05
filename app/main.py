from fastapi import FastAPI
from app.api import app


@app.get("/")
def read_root():
    return {"Hello": "World!!"}
