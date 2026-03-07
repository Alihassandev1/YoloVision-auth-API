from database import SessionLocal
from auth.models import User
from auth import schemas, utils, models
from fastapi import HTTPException

def create_user(db: SessionLocal, user: schemas.CreateUser):
    user = models.User(firstName=user.first_name, lastName=user.last_name, username=user.username, email=user.email, password=utils.get_password_hash(user.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def check_existance(db: SessionLocal, user: schemas.CreateUser):
    user = db.query(User).filter(User.email == user.email or User.username == user.username).first()
    msg = True if user else False
    return msg

# def update_user(db: SessionLocal, user: schemas.CreateUser):
#     db_user = db.query(User).filter(User.id == user.id).first()
#     db_user
#     db.commit()
#     db.refresh(db_user)
#     return user

# def delete_user(db: SessionLocal, user_id: int):
#     user = db.query(User).filter(User.id == user_id).first()
#     db.delete(user)
#     db.commit()
#     return user
