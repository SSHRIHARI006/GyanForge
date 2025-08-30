from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.models import User
from app.core.security import get_current_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": getattr(current_user, 'full_name', current_user.email.split('@')[0]),
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

@router.get("/{user_id}/modules")
async def get_user_modules(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all modules for a specific user"""
    # Ensure user can only access their own modules
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get user's modules - this would need to be implemented based on your database schema
    # For now, return empty list
    return []
