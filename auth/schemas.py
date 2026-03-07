from pydantic import BaseModel
from typing import Optional

class CreateUser(BaseModel):
    first_name: str
    last_name: Optional[str]
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email : str
    password : str

class AccessToken(BaseModel):
    access_token: str
    type : str

class UserResponse(BaseModel):
    id: int
    username: str
    firstName: str
    lastName: Optional[str]
    email: Optional[str]
    is_superuser: Optional[bool] = False
    
    class Config:
        from_attributes = True
