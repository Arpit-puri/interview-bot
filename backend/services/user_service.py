from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from config.database import db
from config.auth import verify_password, get_password_hash
from config.constants import USERS_COLLECTION
from models.user import User, UserResponse
from typing import Optional, List

class UserService:
    def __init__(self):
        self.collection_name = USERS_COLLECTION
    
    def _get_collection(self):
        """Get collection with proper error handling"""
        return db.get_collection(self.collection_name)
    
    async def create_user(self, email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create new user account"""
        collection = self._get_collection()
        
        # Check if user already exists
        existing_user = await collection.find_one({"email": email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        password_hash = get_password_hash(password)
        user = User(
            email=email,
            password_hash=password_hash,
            name=name
        )
        
        # Insert user into database
        result = await collection.insert_one(user.dict(by_alias=True))
        
        # Get created user
        created_user = await collection.find_one({"_id": result.inserted_id})
        return created_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        collection = self._get_collection()
        user = await collection.find_one({"email": email})
        
        if not user:
            return None
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        if not verify_password(password, user["password_hash"]):
            return None
        
        # Update last login
        await collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        collection = self._get_collection()
        return await collection.find_one({"email": email})
    
    async def get_user_profile(self, email: str) -> UserResponse:
        """Get user profile (safe response)"""
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.from_user(user)
    
    async def add_session_to_user(self, email: str, session_id: str):
        """Add session ID to user's sessions list"""
        collection = self._get_collection()
        await collection.update_one(
            {"email": email},
            {"$addToSet": {"sessions": session_id}}  # addToSet prevents duplicates
        )
    
    async def get_user_sessions(self, email: str) -> List[str]:
        """Get all session IDs for a user"""
        user = await self.get_user_by_email(email)
        return user.get("sessions", []) if user else []
    
    async def update_user_profile(self, email: str, name: Optional[str] = None) -> UserResponse:
        """Update user profile"""
        collection = self._get_collection()
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        
        await collection.update_one(
            {"email": email},
            {"$set": update_data}
        )
        
        return await self.get_user_profile(email)

# Global user service instance
user_service = UserService()