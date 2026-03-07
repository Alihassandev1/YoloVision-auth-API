from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from database import SessionLocal
from fastapi import Depends, HTTPException
from auth import models, utils, crud, schemas
from auth.models import User
from jose import JWTError, jwt
import hashlib

oath2_scheme = HTTPBearer()
SECRET_KEY = "213452345yt324tyrhtwergfndgtwtrhgnrtrtt4423t4t423rtt43trhtetht"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hash_password:str):
    return pwd_context.verify(plain_password, hash_password)

def create_user_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def current_user(token: HTTPAuthorizationCredentials = Depends(oath2_scheme)):
    credential_exception = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Step 1: Decode and validate the JWT token
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credential_exception
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credential_exception

    # Step 2: Fetch the user from the database
    # NOTE: We do NOT catch HTTPException here so that proper error responses propagate.
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
    except Exception as e:
        print(f"Error fetching user from DB: {e}")
        raise credential_exception
    finally:
        db.close()

    # Step 3: Validate that the user actually exists
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found or session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def user_authentication(user: schemas.LoginUser, db : SessionLocal):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    access_token = create_user_token(data={"id": db_user.id})
    return {"Access Token" : access_token, "Token Type": "Bearer"}  

