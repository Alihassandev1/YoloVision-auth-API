from ultralytics import YOLO
from fastapi import Depends, File, UploadFile
from database import SessionLocal
from auth.models import UserHistory
from fastapi.responses import FileResponse
from auth.routes import get_db
from PIL import Image
import io
import os

detect_model = YOLO("models/yolo26n.pt")
segment_model = YOLO("models/yolo26n-seg.pt")
classify_model = YOLO("models/yolo26n-cls.pt")
pose_model = YOLO("models/yolo26n-pose.pt")


def detect(img, file_name, user_id):
    results = detect_model(img)
    curr_path = f"Images/{user_id}/detection/{file_name}"
    results[0].save(filename=curr_path)
    return curr_path

def segment(img, file_name, user_id):
    results = segment_model(img)
    curr_path = f"Images/{user_id}/segmention/{file_name}"
    results[0].save(filename=curr_path)
    return curr_path

def classify(img, file_name, user_id):
    results = classify_model(img)
    curr_path = f"Images/{user_id}/classification/{file_name}"
    results[0].save(filename=curr_path)
    return curr_path

def pose(img, file_name, user_id):
    results = pose_model(img)
    curr_path = f"Images/{user_id}/pose/{file_name}"
    results[0].save(filename=curr_path)
    return curr_path

async def perform_model(db: SessionLocal, user, typeo: str, file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename
    img = io.BytesIO(contents)
    image = Image.open(img)
    if typeo == 'Classification':
        model_perform = classify(image, file_name=filename, user_id=user.id)
    elif typeo == 'Detection':
        model_perform = detect(image, file_name=filename, user_id=user.id)
    elif typeo == 'Segmentation':
        model_perform = segment(image, file_name=filename, user_id=user.id)
    elif typeo == 'Pose':
        model_perform = pose(image, file_name=filename, user_id=user.id)
    userHistory = UserHistory(images=model_perform, user_id=user.id, img_type=typeo)
    db.add(userHistory)
    db.commit()
    db.refresh(userHistory)
    return FileResponse(model_perform)