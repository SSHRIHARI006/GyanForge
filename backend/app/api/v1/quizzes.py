from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_session
from app.models.models import UserProgress, LearningModule, User

router = APIRouter(
    prefix="/api/v1/quizzes",
    tags=["quizzes"]
)


class QuizSubmission(BaseModel):
    user_id: int
    module_id: int
    answers: Dict[str, Any]  # Question ID -> Answer


class QuizResult(BaseModel):
    score: float
    feedback: Dict[str, str]  # Question ID -> Feedback
    next_steps: str
    recommended_module_id: Optional[int] = None


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    submission: QuizSubmission,
    session: Session = Depends(get_session)
):
    """
    Submit a quiz for grading and track user progress.
    
    Args:
        submission: Quiz submission data
        session: Database session
        
    Returns:
        Quiz result with score and feedback
    """
    # Get the module
    module = session.get(LearningModule, submission.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {submission.module_id} not found"
        )
    
    # Check if user exists
    user = session.get(User, submission.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {submission.user_id} not found"
        )
    
    # Grade the quiz
    score, feedback = await _grade_quiz(module.quiz_data, submission.answers)
    
    # Update or create user progress
    existing_progress = session.exec(
        select(UserProgress).where(
            (UserProgress.user_id == submission.user_id) &
            (UserProgress.module_id == submission.module_id)
        )
    ).first()
    
    if existing_progress:
        # Update existing progress
        existing_progress.quiz_score = score
        existing_progress.quiz_completed_at = datetime.utcnow()
        session.add(existing_progress)
    else:
        # Create new progress record
        progress = UserProgress(
            user_id=submission.user_id,
            module_id=submission.module_id,
            quiz_score=score,
            quiz_completed_at=datetime.utcnow()
        )
        session.add(progress)
    
    session.commit()
    
    # Determine next steps and recommended module
    next_steps, recommended_module_id = await _determine_next_steps(
        user_id=submission.user_id, 
        module_id=submission.module_id,
        score=score,
        session=session
    )
    
    return QuizResult(
        score=score,
        feedback=feedback,
        next_steps=next_steps,
        recommended_module_id=recommended_module_id
    )


async def _grade_quiz(quiz_data: str, answers: Dict[str, Any]) -> tuple[float, Dict[str, str]]:
    """
    Grade a quiz submission.
    
    Args:
        quiz_data: JSON string containing quiz questions and correct answers
        answers: User's answers
        
    Returns:
        Tuple of (score, feedback)
    """
    import json
    
    try:
        quiz = json.loads(quiz_data)
        questions = quiz.get("questions", [])
        
        if not questions:
            return 0.0, {"error": "No questions found in quiz data"}
        
        correct_count = 0
        feedback = {}
        
        for i, question in enumerate(questions):
            question_id = question.get("id", str(i))
            correct_answer = question.get("correct_answer")
            user_answer = answers.get(question_id)
            
            if user_answer == correct_answer:
                correct_count += 1
                feedback[question_id] = "Correct!"
            else:
                explanation = question.get("explanation", "")
                feedback[question_id] = f"Incorrect. {explanation}"
        
        score = (correct_count / len(questions)) * 100
        return score, feedback
        
    except Exception as e:
        return 0.0, {"error": f"Error grading quiz: {str(e)}"}


async def _determine_next_steps(user_id: int, module_id: int, score: float, session: Session) -> tuple[str, Optional[int]]:
    """
    Determine next steps and recommended module based on quiz score.
    
    In a full implementation, this would use your LangChain agent for adaptive learning path.
    
    Args:
        user_id: User ID
        module_id: Current module ID
        score: Quiz score
        session: Database session
        
    Returns:
        Tuple of (next_steps, recommended_module_id)
    """
    # This is a simplified implementation
    # In reality, you would use your LangChain agent to determine the next module
    
    if score >= 80:
        # User did well, move to next topic
        return "Great job! You're ready to move on to the next topic.", None
    elif score >= 50:
        # User did okay, recommend practice
        return "You're getting there! Try some practice exercises before moving on.", None
    else:
        # User struggled, recommend reviewing the same topic
        return "It looks like you need more practice with this topic. Try reviewing the material again.", module_id
