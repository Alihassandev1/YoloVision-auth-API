from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from yolomodels.utils import perform_model
from auth.utils import current_user
from admin.routes import get_db

router = APIRouter()

@router.post("/upload-detection-image")
async def image_detection(file: UploadFile = File(...), user: dict = Depends(current_user), db : Session = Depends(get_db)):
    return await perform_model(db, user, 'Detection', file)

@router.post("/upload-segmentation-image")
async def image_segmentation(file: UploadFile = File(...), user: dict = Depends(current_user), db : Session = Depends(get_db)):
    return await perform_model(db, user, 'Segmentation', file)

@router.post("/upload-classification-image")
async def image_classification(file: UploadFile = File(...), user: dict = Depends(current_user), db : Session = Depends(get_db)):
    return await perform_model(db, user, 'Classification', file)

@router.post("/upload-pose-image")
async def image_pose(file: UploadFile = File(...), user: dict = Depends(current_user), db: Session = Depends(get_db)):
    return await perform_model(db, user, 'Pose', file)