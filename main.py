from typing import Annotated
from fastapi import FastAPI, Path, Query, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from auth import models
from auth.routes import router as auth_routes
from admin.routes import router as admin_routes
from yolomodels.routes import router as yolomodels_routes

models.Base.metadata.create_all(bind=engine)  # uses auth.models.Base

app = FastAPI(version='2.0.1')

@app.get("/")
def read_root():
    return {"Hello": "World"}

# other apps routers
app.include_router(auth_routes, prefix="/auth", tags=["Authentication"])
app.include_router(admin_routes, prefix="/admin", tags=["Admin"])
app.include_router(yolomodels_routes, prefix="/yoloModels", tags=["Yolo Models"])

# uvicorn.run(app, host='127.0.0.1', port=8000)