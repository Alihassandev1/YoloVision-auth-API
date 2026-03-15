from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from admin import crud, schemas
from auth.crud import check_existance, create_user
import auth
from auth.utils import current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users/", response_model=list[schemas.UserResponse])
async def read_all_users_profiles(db: Session = Depends(get_db), user: dict = Depends(current_user)):
    # if user["role"] != "admin":
    #     raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    users = crud.get_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No User Has Been Registered Yet")
    return users

@router.get("/user/{user_id}", response_model=schemas.UserResponse)
async def read_user_by_id(user_id: int, db: Session = Depends(get_db), user: dict = Depends(current_user)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/user", response_model=schemas.UserResponse)
async def create_new_user(user: schemas.CreateUser, db: Session = Depends(get_db), auth_user: dict = Depends(current_user)):
    db_user = check_existance(db, user)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.put("/user/me", response_model=schemas.UserResponse)
async def update_user(user: schemas.UpdateUser, old_user: schemas.UserResponse = Depends(auth.utils.current_user), db: Session = Depends(get_db)):
    return crud.update_user(db, user, old_user)

@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(current_user)):
    return crud.delete_user(db, user_id)
