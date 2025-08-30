from fastapi import APIRouter, HTTPException
from models.requests import ChatRequest
from controllers.chat_controller import chat_controller

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/send")
async def send_message(request: ChatRequest):
    """Send a message during the interview"""
    try:
        return await chat_controller.send_message(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.post("/stream")
async def stream_message(request: ChatRequest):
    try:
        return await chat_controller.stream_message(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")