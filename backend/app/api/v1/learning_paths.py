from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, List, Optional, Any

from app.db.session import get_session
from app.core.security import get_current_user
from app.services.learning_path_service import LearningPathService
from app.models.models import User
from app.schemas.schemas import LearningPathRequest, LearningPathResponse

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


@router.post("/generate", response_model=LearningPathResponse)
async def generate_learning_path(
    request: LearningPathRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a personalized learning path based on user's goals and progress.
    """
    learning_path_service = LearningPathService(db_session=db)
    
    # Call the learning path service
    result = learning_path_service.generate_learning_path(
        user_id=current_user.id, 
        topic=request.topic_area, 
        goal_description=request.goal_description
    )
    
    # Check for errors
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
        
    return result
