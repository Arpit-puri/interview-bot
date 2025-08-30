from fastapi import HTTPException
from models.requests import SessionRequest, StartInterviewRequest, EndInterviewRequest
from models.session import Message
from services.session_service import session_service
from services.ai_service import ai_service
from models.user import UserSessionSummary
from services.user_service import user_service
from typing import Optional, List

class SessionController:
    """Controller for handling session-related business logic"""
    
    @staticmethod
    async def init_session(request: SessionRequest,  current_user_email: Optional[str] = None):
        """Initialize a new interview session"""
        session_id = await session_service.create_session(request.role_id)
        if current_user_email:
            await user_service.add_session_to_user(current_user_email, session_id)
        return {"session_id": session_id}
    
    @staticmethod
    async def get_history(session_id: str,  current_user_email: Optional[str] = None):
        """Get chat history for a session"""
        messages = await session_service.get_session_messages(session_id)
        return messages
    
    @staticmethod
    async def get_session_status(session_id: str,  current_user_email: Optional[str] = None):
        """Get current session status"""
        status = await session_service.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        return status
    
    @staticmethod
    async def start_interview(request: StartInterviewRequest,  current_user_email: Optional[str] = None):
        """Start the interview"""
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add initial greeting message
        greeting_msg = Message(role="user", content="Hello! I'm ready to start my interview.")
        await session_service.add_message(request.session_id, greeting_msg)
        
        # Get updated session for AI processing
        updated_session = await session_service.get_session(request.session_id)
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in updated_session["messages"]]
        
        # Generate AI response
        reply = await ai_service.generate_response(messages)
        assistant_msg = Message(role="assistant", content=reply)
        # Add assistant response and update metadata
        await session_service.add_message(request.session_id, assistant_msg)
        await session_service.update_metadata(request.session_id, {
            "question_count": 1,
            "current_phase": "greeting"
        })
        
        return {"response": reply}
    
    @staticmethod
    async def end_interview(request: EndInterviewRequest,  current_user_email: Optional[str] = None):
        """Manually end the interview"""
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Mark interview as completed
        await session_service.mark_interview_completed(request.session_id, manually_ended=True)
        
        # Add final message
        final_message = Message(
            role="assistant", 
            content="Thank you for taking the time to interview with us! While we didn't complete all questions, you've provided valuable insights. We appreciate your participation and will be in touch regarding next steps. Have a great day! 🎯"
        )
        await session_service.add_message(request.session_id, final_message)
        
        return {"response": final_message.content, "interview_ended": True}

    @staticmethod
    async def get_user_sessions(current_user_email: str) -> List[UserSessionSummary]:
        """Get all sessions for a user"""
        session_ids = await user_service.get_user_sessions(current_user_email)
        
        sessions_data = []
        for session_id in session_ids:
            session = await session_service.get_session(session_id)
            if session:
                metadata = session.get("metadata", {})
                sessions_data.append(UserSessionSummary(
                    session_id=session_id,
                    role_id=session["role_id"],
                    created_at=metadata.get("created_at", session.get("created_at")),
                    question_count=metadata.get("question_count", 0),
                    current_phase=metadata.get("current_phase", "greeting"),
                    interview_completed=metadata.get("interview_completed", False),
                    manually_ended=metadata.get("manually_ended", False),
                    progress_percentage=min((metadata.get("question_count", 0) / 20) * 100, 100)
                ))
        
        return sessions_data
    
    @staticmethod
    async def get_user_active_sessions(current_user_email: str) -> List[UserSessionSummary]:
        """Get active (incomplete) sessions for a user"""
        all_sessions = await SessionController.get_user_sessions(current_user_email)
        return [session for session in all_sessions if not session.interview_completed]

# Global controller instance
session_controller = SessionController()
