from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from auth import schemas, models, crud, utils
from auth.utils import create_user_token

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register/")
async def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=404, detail="Enter Details First!")
    existing_user = crud.check_existance(db, user)
    if(existing_user):
        raise HTTPException(status_code=404, detail= "User is already Registered!")
    user = crud.create_user(db, user)
    if not user:
        raise HTTPException(status_code=404, detail="Registeration Failed!")
    access_token = create_user_token(data={"id": user.id})
    return {
        "msg":"CONGRATULATIONS! User Registered Successfully",
        "Access Token": access_token
        }

@router.post('/login')
async def authenticate_user(user: schemas.LoginUser, db: Session = Depends(get_db)):
    if not utils.user_authentication(user, db):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    return utils.user_authentication(user, db)

@router.get("/me", response_model=schemas.UserResponse)

async def my_profile(user: schemas.UserResponse = Depends(utils.current_user)):
    return user

@router.post("/me/update-password")
async def update_your_password(old_password: str, new_password: str, user: schemas.UserResponse = Depends(utils.current_user), db: Session = Depends(get_db)):
    register_password = user.password
    if not utils.verify_password(old_password, register_password):
        raise HTTPException(status_code=404, detail="Invalid Password")
    new_password_hash = utils.get_password_hash(new_password)
    db.query(User).filter(User.id == user.id).update({User.password: new_password_hash})
    db.commit()
    db.refresh(user)
    return "Congratulations! Password Changed Successfully"

@router.post("/superuser", response_model=schemas.UserResponse)
async def create_superuser(user: schemas.CreateUser, db: Session = Depends(get_db)):
    return user