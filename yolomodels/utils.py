from ultralytics import YOLO
from fastapi import Depends, File, UploadFile
from database import SessionLocal
from auth.models import UserHistory
from fastapi.responses import FileResponse
from pathlib import PureWindowsPath
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
    curr_path = f"images/{user_id}/detection/{file_name}"
    results[0].save(filename=curr_path)
    return curr_path

def segment(img, file_name, user_id):
    results = segment_model(img)
    curr_path = f"images/{user_id}/segmention/{filename}"
    results[0].save(filename=curr_path)
    return curr_path

def classify(img, file_name, user_id):
    results = classify_model(img)
    curr_path = f"images/{user_id}/classified_images/{filename}"
    results[0].save(filename=curr_path)
    return curr_path

def pose(img, file_name, user_id):
    results = pose_model(img)
    curr_path = f"images/{user_id}/posed_images/{filename}"
    results[0].save(filename=curr_path)
    return curr_path
