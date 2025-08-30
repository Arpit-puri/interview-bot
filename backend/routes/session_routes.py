from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from models.requests import SessionRequest, StartInterviewRequest, EndInterviewRequest
from controllers.session_controller import session_controller
from config.auth import get_current_user_email

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

async def get_optional_user_email(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Get user email from token if provided, otherwise return None (for guest users)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        from fastapi.security import HTTPAuthorizationCredentials
        from config.auth import verify_token
        token = authorization.replace("Bearer ", "")
        return verify_token(token)
    except:
        return None  # Invalid token = guest user

@router.post("/init")
async def init_session(
    request: SessionRequest,
    current_user_email: Optional[str] = Depends(get_optional_user_email)
):
    """Initialize a new interview session (supports both authenticated and guest users)"""
    try:
        return await session_controller.init_session(request, current_user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/{session_id}/history")
async def get_history(
    session_id: str,
    current_user_email: Optional[str] = Depends(get_optional_user_email)
):
    """Get chat history for a session"""
    try:
        return await session_controller.get_history(session_id, current_user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user_email: Optional[str] = Depends(get_optional_user_email)
):
    """Get current session status"""
    try:
        return await session_controller.get_session_status(session_id, current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/start")
async def start_interview(
    request: StartInterviewRequest,
    current_user_email: Optional[str] = Depends(get_optional_user_email)
):
    """Start the interview"""
    try:
        return await session_controller.start_interview(request, current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@router.post("/end")
async def end_interview(
    request: EndInterviewRequest,
    current_user_email: Optional[str] = Depends(get_optional_user_email)
):
    """Manually end the interview"""
    try:
        return await session_controller.end_interview(request, current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end interview: {str(e)}")

# NEW: User-specific routes (require authentication)
@router.get("/my-sessions")
async def get_my_sessions(current_user_email: str = Depends(get_current_user_email)):
    """Get all sessions for the authenticated user"""
    try:
        return await session_controller.get_user_sessions(current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user sessions: {str(e)}")

@router.get("/my-sessions/active")
async def get_my_active_sessions(current_user_email: str = Depends(get_current_user_email)):
    """Get active (incomplete) sessions for the authenticated user"""
    try:
        return await session_controller.get_user_active_sessions(current_user_email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active sessions: {str(e)}")