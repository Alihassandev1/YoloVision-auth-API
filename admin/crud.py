from auth.models import User
from fastapi import Depends
from database import SessionLocal
from fastapi import HTTPException
from admin import schemas
import auth

def get_users(db: SessionLocal):
    return db.query(User).all()

def get_user(db: SessionLocal, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(db: SessionLocal, user: schemas.UpdateUser, old_user: schemas.UserResponse = Depends(auth.utils.current_user)):
    if user.username is not None:
        old_user.username = user.username
    if user.email is not None:
        old_user.email = user.email
    if user.first_name is not None:
        old_user.first_name = user.first_name
    if user.last_name is not None:
        old_user.last_name = user.last_name
    db.commit()
    db.refresh(old_user)
    return old_user

def delete_user(db: SessionLocal, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return f"{user.username} User Deleted Successfully"