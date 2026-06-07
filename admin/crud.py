from auth.models import User
from database import SessionLocal
from fastapi import HTTPException, UploadFile
import aiofiles
import shutil

def get_users(db: SessionLocal):
    return db.query(User).all()

def get_user(db: SessionLocal, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(db: SessionLocal, old_user: User, fn: str | None = None, ln: str | None = None, un: str | None = None, em: str | None = None):
    if em:
        existing_email_user = db.query(User).filter(
            User.email == em,
            User.id != old_user.id  # exclude the current user
        ).first()
        if existing_email_user:
            raise HTTPException(status_code=400, detail="Email already in use")

    # Check for duplicate username
    if un:
        existing_username_user = db.query(User).filter(
            User.username == un,
            User.id != old_user.id
        ).first()
        if existing_username_user:
            raise HTTPException(status_code=400, detail="Username already in use")
    
    if un is not None:
        db.query(User).filter(User.id == old_user.id).update({User.username: un})
    if em is not None:
        db.query(User).filter(User.id == old_user.id).update({User.email: em})
    if fn is not None:
        db.query(User).filter(User.id == old_user.id).update({User.firstName: fn})
    if ln is not None:
        db.query(User).filter(User.id == old_user.id).update({User.lastName: ln})
    db.commit()
    return old_user

def delete_user(db: SessionLocal, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return f"{user.username} User Deleted Successfully"