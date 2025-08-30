from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.security import get_current_user
from app.models.models import User
from app.services.simple_chat_service import SimpleChatService as EnhancedChatService

router = APIRouter(prefix="/api/v1", tags=["chat"])

# Initialize enhanced chat service
chat_service = EnhancedChatService()

class ChatMessage(BaseModel):
    message: str
    current_module: Optional[str] = None

@router.post("/chat")
async def chat_with_ai(
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """Chat with AI assistant with learning context"""
    try:
        response = chat_service.chat_with_context(
            user_id=current_user.id,
            message=chat_request.message,
            current_module=chat_request.current_module
        )
        
        return {
            "success": True,
            "response": response["response"],
            "suggestions": response.get("suggestions", []),
            "learning_insights": response.get("learning_insights", []),
            "recommended_actions": response.get("recommended_actions", []),
            "context_used": response.get("context_used", False)
        }
        
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

@router.delete("/chat/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user)
):
    """Clear user's chat history"""
    try:
        chat_service.clear_conversation_history(current_user.id)
        
        return {
            "success": True,
            "message": "Chat history cleared successfully"
        }
        
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")

@router.get("/chat/summary")
async def get_chat_summary(
    current_user: User = Depends(get_current_user)
):
    """Get summary of user's chat interactions"""
    try:
        summary = chat_service.get_conversation_summary(current_user.id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        print(f"Error getting chat summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat summary")
