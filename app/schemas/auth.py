from pydantic import BaseModel,EmailStr
from typing import Optional
import uuid

# Register
class RegisterRequest(BaseModel):
    name:str
    phone:str
    email:EmailStr
    password:str

# Login
class LoginRequest(BaseModel):
    email:EmailStr
    password:str

# Google Auth
class GoogleAuthRequest():
    id_token:str

class AuthResponse():
    access_token:str
    token_type:str = "bearer"
    user:"UserResponse"

class UserResponse():
    id:uuid.UUID
    name:str
    email:str
    phone:Optional[str]
    profile_pic:Optional[str]
    is_admin:bool
    auth_provider:str

    class config:
        from_attributes=True