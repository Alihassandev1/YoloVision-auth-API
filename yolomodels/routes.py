from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from trt import detect, segment, classify, pose
from auth.utils import current_user
from auth.models import UserHistory
from admin.routes import get_db
import io
from PIL import Image

router = APIRouter()

@router.post("/upload-detection-image")
async def image_detection(file: UploadFile = File(...), user: dict = Depends(current_user), db : Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    img = io.BytesIO(contents)
    image = Image.open(img)
    detection = detect(image, filename, user.id)
    userHistory = UserHistory(images=detection, user_id=user.id, img_type='Detection')
    db.add(userHistory)
    db.commit()
    db.refresh(userHistory)
    return FileResponse(detection)

@router.post("/upload-segmentation-image")
async def image_segmentation(file: UploadFile = File(...), user: dict = Depends(current_user), db : Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    img = io.BytesIO(contents)
    image = Image.open(img)
    segmentation = segment(img, filename)
    userHistory = UserHistory(images=segmentation, user_id=user.id, img_type='Segmentation')
    db.add(userHistory)
    db.commit()
    db.refresh(userHistory)
    return FileResponse(segmentation)

@router.post("/upload-classification-image")
async def image_classification(file: UploadFile = File(...), user: dict = Depends(current_user)):
    contents = await file.read()
    filename = file.filename
    img = io.BytesIO(contents)
    image = Image.open(img)
    classification = classify(img, file_name=filename)
    userHistory = UserHistory(images=classification, user_id=user.id, img_type='Classification')
    db.add(userHistory)
    db.commit()
    db.refresh(userHistory)
    return FileResponse(classification)

@router.post("/upload-pose-image")
async def image_pose(file: UploadFile = File(...), user: dict = Depends(current_user)):
    contents = await file.read()
    filename = file.filename
    img = io.BytesIO(contents)
    image = Image.open(img)
    posed = segment(img, file_name=filename)
    userHistory = UserHistory(images=posed, user_id=user.id, img_type='Posed')
    db.add(userHistory)
    db.commit()
    db.refresh(userHistory)
    return FileResponse(posed)

