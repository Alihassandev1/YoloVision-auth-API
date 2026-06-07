from pydantic import BaseModel
from typing import Optional
from auth.schemas import CreateUser, LoginUser, AccessToken, UserResponse

class UpdateUser(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
