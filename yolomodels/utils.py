from ultralytics import YOLO
from fastapi import Depends, File, UploadFile, HTTPException
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


def mode(img, file_name, user_id, method):
    if method == "Detection":
        results = detect_model(img)
    elif method == "Segmentation":
        results = segment_model(img)
    elif method == "Classification":
        results = classify_model(img)
    elif method == "Pose":
        results = pose_model(img)
    curr_path = f"Images/{user_id}/{method}/{file_name}"
    results[0].save(filename=curr_path)
    return curr_path


def detect(img, file_name, user_id):
    results = detect_model(img)
    curr_path = f"Images/{user_id}/detection/{file_name}"
    os.makedirs(os.path.dirname(curr_path), exist_ok=True)
    results[0].save(filename=curr_path)
    return curr_path

def segment(img, file_name, user_id):
    results = segment_model(img)
    curr_path = f"Images/{user_id}/segmentation/{file_name}"
    os.makedirs(os.path.dirname(curr_path), exist_ok=True)
    results[0].save(filename=curr_path)
    return curr_path

def classify(img, file_name, user_id):
    results = classify_model(img)
    curr_path = f"Images/{user_id}/classification/{file_name}"
    os.makedirs(os.path.dirname(curr_path), exist_ok=True)
    results[0].save(filename=curr_path)
    return curr_path

def pose(img, file_name, user_id):
    results = pose_model(img)
    curr_path = f"Images/{user_id}/pose/{file_name}"
    os.makedirs(os.path.dirname(curr_path), exist_ok=True)
    results[0].save(filename=curr_path)
    return curr_path

async def perform_model(db: SessionLocal, user, typeo: str, file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename
    if not filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    img_buf = io.BytesIO(contents)
    try:
        temp_image = Image.open(img_buf)
        temp_image.verify() 
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    img_buf.seek(0)
    image = Image.open(img_buf)

    if typeo == 'Classification':
        model_perform = classify(img=image, file_name=filename, user_id=user.id)
    elif typeo == 'Detection':
        model_perform = detect(img=image, file_name=filename, user_id=user.id)
    elif typeo == 'Segmentation':
        model_perform = segment(img=image, file_name=filename, user_id=user.id)
    elif typeo == 'Pose':
        model_perform = pose(img=image, file_name=filename, user_id=user.id)
    else:
        raise HTTPException(status_code=400, detail="Unknown model type")
    
    userHistory = UserHistory(images=model_perform, user_id=user.id, img_type=typeo)
    db.add(userHistory)
    db.commit()
    db.refresh(userHistory)
    return FileResponse(model_perform)