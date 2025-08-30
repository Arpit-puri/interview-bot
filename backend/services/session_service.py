from typing import Optional, List, Dict, Any
from datetime import datetime
from config.database import db
from config.constants import SESSIONS_COLLECTION, TOTAL_QUESTIONS
from models.session import Session, Message, SessionMetadata
from data.role_prompts import ROLE_PROMPTS

class SessionService:
    def __init__(self):
        self.collection_name = SESSIONS_COLLECTION
    
    def _get_collection(self):
        """Get collection with proper error handling"""
        return db.get_collection(self.collection_name)
    
    async def create_session(self, role_id: str) -> str:
        """Create a new interview session"""
        import uuid
        
        session_id = str(uuid.uuid4())
        role_prompt = ROLE_PROMPTS.get(role_id, ROLE_PROMPTS["meta-ads-expert"])
        
        session = Session(
            session_id=session_id,
            role_id=role_id,
            messages=[Message(**role_prompt)]
        )
        
        collection = self._get_collection()
        await collection.insert_one(session.dict(by_alias=True))
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by session_id"""
        collection = self._get_collection()
        return await collection.find_one({"session_id": session_id})
    
    async def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session messages (excluding system prompt)"""
        session = await self.get_session(session_id)
        if session:
            return [msg for msg in session["messages"] if msg["role"] != "system"]
        return []
    
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to the session"""
        collection = self._get_collection()
        await collection.update_one(
            {"session_id": session_id},
            {"$push": {"messages": message.dict()}}
        )
    
    async def update_metadata(self, session_id: str, metadata_updates: Dict[str, Any]) -> None:
        """Update session metadata"""
        metadata_updates["updated_at"] = datetime.utcnow()
        collection = self._get_collection()
        await collection.update_one(
            {"session_id": session_id},
            {"$set": {f"metadata.{k}": v for k, v in metadata_updates.items()}}
        )
    
    async def mark_interview_completed(self, session_id: str, manually_ended: bool = False) -> None:
        """Mark interview as completed"""
        await self.update_metadata(session_id, {
            "interview_completed": True,
            "manually_ended": manually_ended
        })
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        metadata = session.get("metadata", {})
        question_count = metadata.get("question_count", 0)
        current_phase = self._determine_current_phase(question_count)
        
        return {
            "question_count": question_count,
            "current_phase": current_phase,
            "total_questions": TOTAL_QUESTIONS,
            "interview_completed": metadata.get("interview_completed", False),
            "manually_ended": metadata.get("manually_ended", False),
            "progress_percentage": min((question_count / TOTAL_QUESTIONS) * 100, 100)
        }
    
    def _determine_current_phase(self, question_count: int) -> str:
        """Determine current interview phase based on question count"""
        if question_count <= 1:
            return "greeting"
        elif question_count <= 8:  # 1 greeting + 7 easy
            return "easy"
        elif question_count <= 12:  # + 4 moderate
            return "moderate"
        elif question_count <= 14:  # + 2 scenario
            return "scenario"
        elif question_count <= 17:  # + 3 hard
            return "hard"
        elif question_count <= 19:  # + 2 expert
            return "expert"
        else:
            return "completed"
    
    async def add_message_and_update_metadata(self, session_id: str, message: Message, metadata_updates: dict):
        """
        Atomically add message and update metadata in single database operation
        """
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message.dict()},
                    "$set": {
                        **{f"metadata.{key}": value for key, value in metadata_updates.items()},
                        "metadata.updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Session {session_id} not found")
                
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error adding message and updating metadata: {e}")
            raise
# Global session service instance
session_service = SessionService()
