from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from models.requests import ChatRequest
from models.session import Message
from services.session_service import session_service
from services.ai_service import ai_service, RateLimitExceeded
from config.constants import TOTAL_QUESTIONS

class ChatController:
    """Controller for handling chat-related business logic"""

    @staticmethod
    async def send_message(request: ChatRequest):
        # Get session and check if it exists
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if interview is already completed
        metadata = session.get("metadata", {})
        if metadata.get("interview_completed", False):
            raise HTTPException(status_code=400, detail="Interview has already been completed")

        # Add user message
        user_msg = Message(role="user", content=request.message)
        await session_service.add_message(request.session_id, user_msg)

        # Increment question count after user response
        current_question_count = metadata.get("question_count", 0) + 1
        current_phase = session_service._determine_current_phase(current_question_count)

        # Check if we've reached the question limit
        if current_question_count >= TOTAL_QUESTIONS:
            await session_service.mark_interview_completed(request.session_id)
            final_response = (
                "Thank you for completing the full interview! You've answered all questions across "
                "different difficulty levels. This gives us a comprehensive understanding of your expertise. "
                "We appreciate your time and detailed responses. We'll review your performance and get back to you soon! 🎯✨"
            )
            final_msg = Message(role="assistant", content=final_response)
            await session_service.add_message(request.session_id, final_msg)
            return {"response": final_response, "interview_completed": True}

        # Get updated session for AI processing
        updated_session = await session_service.get_session(request.session_id)
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in updated_session["messages"]]

        # Phase context
        phase_context = f"CURRENT STATUS: Question {current_question_count}/{TOTAL_QUESTIONS}, Phase: {current_phase.upper()}"

        try:
            reply = await ai_service.generate_response(messages, phase_context)
            assistant_msg = Message(role="assistant", content=reply)

            await session_service.add_message(request.session_id, assistant_msg)
            await session_service.update_metadata(request.session_id, {
                "question_count": current_question_count,
                "current_phase": current_phase
            })

            return {"response": reply}

        except RateLimitExceeded as e:
            # Rate limit exceeded - return 429 status
            raise HTTPException(
                status_code=429, 
                detail={
                    "message": str(e),
                    "retry_after": 60,  # seconds
                    "type": "rate_limit_exceeded"
                }
            )
        
        except ValueError as e:
            # API key missing - server configuration error
            print(f"AI Service configuration error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Service temporarily unavailable. Please contact support if this persists."
            )
        
        except Exception as e:
            # All other errors (timeouts, API failures, network issues, etc.)
            print(f"AI Service error: {e}")
            
            # Save an error message to maintain conversation flow
            error_response = "Sorry, I'm experiencing some technical difficulties right now. Please try again in a moment."
            assistant_msg = Message(role="assistant", content=error_response)
            await session_service.add_message(request.session_id, assistant_msg)
            
            raise HTTPException(
                status_code=503, 
                detail={
                    "message": error_response,
                    "type": "service_error"
                }
            )

    @staticmethod
    async def stream_message(request: ChatRequest):
        """Stream AI response token-by-token (keeps context)"""
        # 1) Session checks
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        metadata = session.get("metadata", {})
        if metadata.get("interview_completed", False):
            raise HTTPException(status_code=400, detail="Interview has already been completed")

        # 2) Save user message ONCE
        user_msg = Message(role="user", content=request.message)
        await session_service.add_message(request.session_id, user_msg)

        # 3) Counters / phase
        current_question_count = metadata.get("question_count", 0) + 1
        current_phase = session_service._determine_current_phase(current_question_count)

        # 4) Handle completion
        if current_question_count >= TOTAL_QUESTIONS:
            await session_service.mark_interview_completed(request.session_id)
            final_response = (
                "Thank you for completing the full interview! "
                "We appreciate your time and detailed responses."
            )
            final_msg = Message(role="assistant", content=final_response)
            await session_service.add_message(request.session_id, final_msg)

            async def final_stream():
                yield final_response
            return StreamingResponse(final_stream(), media_type="text/plain")

        # 5) Build messages (with system prompt preserved)
        updated_session = await session_service.get_session(request.session_id)
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in updated_session["messages"]]

        phase_context = (
            f"CURRENT STATUS: Question {current_question_count}/{TOTAL_QUESTIONS}, "
            f"Phase: {current_phase.upper()}"
        )

        # 6) Accumulate streamed tokens - NO database writes during streaming
        accumulated_response = ""

        async def streaming_with_save():
            nonlocal accumulated_response
            
            try:
                # Stream tokens without any database operations - WITH ERROR HANDLING
                async for token in ai_service.stream_response(messages, phase_context):
                    accumulated_response += token
                    yield token  # Only yield to client, NO database writes
                    
            except RateLimitExceeded as e:
                # Handle rate limiting during streaming
                error_msg = "Rate limit exceeded. Please wait a moment before continuing the conversation."
                accumulated_response = error_msg
                yield error_msg
                print(f"Streaming rate limit error: {e}")
                
            except Exception as e:
                # Handle other streaming errors
                error_msg = "Sorry, I encountered a technical issue. Please try sending your message again."
                accumulated_response = error_msg
                yield error_msg
                print(f"Streaming error: {e}")
                
            finally:
                # Save ONCE when streaming completes (or client disconnects)
                if accumulated_response.strip():
                    assistant_msg = Message(role="assistant", content=accumulated_response)
                    
                    try:
                        # Single database operation with both message and metadata
                        await session_service.add_message_and_update_metadata(
                            request.session_id,
                            assistant_msg,
                            {
                                "question_count": current_question_count,
                                "current_phase": current_phase
                            }
                        )
                    except Exception as db_error:
                        # Log database errors but don't disrupt the stream
                        print(f"Database save error after streaming: {db_error}")

        # Handle initial streaming setup errors (rate limiting check happens here)
        try:
            return StreamingResponse(streaming_with_save(), media_type="text/plain")
            
        except RateLimitExceeded as e:
            # Rate limit exceeded before streaming starts
            raise HTTPException(
                status_code=429, 
                detail={
                    "message": str(e),
                    "retry_after": 60,
                    "type": "rate_limit_exceeded"
                }
            )
        
        except ValueError as e:
            # API key missing - server configuration error
            print(f"AI Service configuration error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Service temporarily unavailable. Please contact support if this persists."
            )

# Global controller instance
chat_controller = ChatController()