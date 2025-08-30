from fastapi import APIRouter, HTTPException, Depends
from models.requests import SignupRequest, LoginRequest, AuthResponse
from models.user import UserResponse
from controllers.auth_controller import auth_controller
from config.auth import get_current_user_email

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """User registration"""
    try:
        return await auth_controller.signup(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=AuthResponse) 
async def login(request: LoginRequest):
    """User login"""
    try:
        return await auth_controller.login(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user_email: str = Depends(get_current_user_email)):
    """Get current user profile (requires authentication)"""
    try:
        return await auth_controller.get_profile(current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.post("/logout")
async def logout(current_user_email: str = Depends(get_current_user_email)):
    """User logout"""
    try:
        return await auth_controller.logout(current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user_email: str = Depends(get_current_user_email)):
    """Get current authenticated user (alias for /profile)"""
    return await auth_controller.get_profile(current_user_email)