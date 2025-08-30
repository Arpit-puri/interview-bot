from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    sessions: List[str] = []
    is_active: bool = True
    is_verified: bool = False 
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ✅ NEW: Public user model (without sensitive data)
class UserResponse(BaseModel):
    """User model for API responses (excludes password_hash)"""
    id: Optional[str] = None
    email: str
    name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    session_count: int = 0  # Calculated field
    is_verified: bool = False
    
    @classmethod
    def from_user(cls, user_dict: dict):
        """Create UserResponse from User document"""
        return cls(
            id=str(user_dict.get("_id")),
            email=user_dict["email"],
            name=user_dict.get("name"),
            created_at=user_dict["created_at"],
            last_login=user_dict.get("last_login"),
            session_count=len(user_dict.get("sessions", [])),
            is_verified=user_dict.get("is_verified", False)
        )

class UserSessionSummary(BaseModel):
    """Session summary for user's session list"""
    session_id: str
    role_id: str
    created_at: datetime
    question_count: int = 0
    current_phase: str = "greeting"
    interview_completed: bool = False
    manually_ended: bool = False
    progress_percentage: float = 0.0