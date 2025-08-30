from pydantic import BaseModel, EmailStr
from typing import Optional

class SessionRequest(BaseModel):
    role_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: str

class StartInterviewRequest(BaseModel):
    session_id: str

class EndInterviewRequest(BaseModel):
    session_id: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class TokenData(BaseModel):
    email: Optional[str] = None