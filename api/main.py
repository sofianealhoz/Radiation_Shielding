from fastapi import FastAPI
from .database import engine, Base
from . import models

models.Base.create_all(bind=engine)

app = FastAPI(title="Shield-Lite API")

@app.get("/")
def read_root():
    return {"message": "Base et tables crées"}