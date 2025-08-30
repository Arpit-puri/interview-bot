from fastapi import HTTPException, status
from models.requests import SignupRequest, LoginRequest, AuthResponse
from models.user import UserResponse
from services.user_service import user_service
from config.auth import create_access_token

class AuthController:
    """Controller for handling authentication business logic"""
    
    @staticmethod
    async def signup(request: SignupRequest) -> AuthResponse:
        """Handle user registration"""
        # Create user
        user = await user_service.create_user(
            email=request.email,
            password=request.password,
            name=request.name
        )
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": request.email})
        
        # Return safe user data
        user_response = UserResponse.from_user(user)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response.dict()
        )
    
    @staticmethod
    async def login(request: LoginRequest) -> AuthResponse:
        """Handle user login"""
        # Authenticate user
        user = await user_service.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": request.email})
        
        # Return safe user data
        user_response = UserResponse.from_user(user)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response.dict()
        )
    
    @staticmethod
    async def get_profile(user_email: str) -> UserResponse:
        """Get current user profile"""
        return await user_service.get_user_profile(user_email)
    
    @staticmethod
    async def logout(user_email: str) -> dict:
        """Handle user logout (JWT is stateless, so just return success)"""
        # Note: JWT tokens are stateless, so logout is handled client-side
        # You could implement token blacklisting here if needed
        return {"message": "Successfully logged out"}

# Global auth controller instance
auth_controller = AuthController()