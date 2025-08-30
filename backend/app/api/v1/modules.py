from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import json

from app.db.session import get_session
from app.models.models import LearningModule, User, UserProgress
from app.services.content_service import content_generation_service
from app.core.security import get_current_user

router = APIRouter(
    prefix="/api/v1/modules",
    tags=["modules"]
)


class ModuleRequest(BaseModel):
    prompt: str
    background_knowledge: Optional[str] = None
    user_id: Optional[int] = None

class ModuleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    video_links: Optional[str] = None
    assignment_url: Optional[str] = None
    quiz_data: Optional[str] = None
    difficulty: Optional[str] = None
    duration: Optional[int] = None
    quiz_questions: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = "active"
    created_at: Optional[str] = None

class QuizSubmission(BaseModel):
    answers: Dict[str, str]

class QuizResult(BaseModel):
    score: float
    total_questions: int
    correct_answers: int
    feedback: List[Dict[str, Any]]
    difficulty: Optional[str] = None
    duration: Optional[int] = None
    quiz_questions: Optional[List[Dict[str, Any]]] = None
    assignment_latex: Optional[str] = None


@router.post("/generate")
async def generate_module(
    request: ModuleRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate a personalized learning module based on user prompt.
    
    Args:
        request: Contains user prompt, background knowledge, and optional user_id
        background_tasks: For asynchronous processing
        session: Database session
        
    Returns:
        The generated learning module
    """
    try:
        # Get user progress if user_id is provided
        user_progress = None
        if request.user_id:
            # Check if user exists
            user = session.get(User, request.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {request.user_id} not found"
                )
            
            # Get user's progress history
            progress_items = session.query(UserProgress).filter(
                UserProgress.user_id == request.user_id
            ).all()
            
            # Format progress for the content generation service
            user_progress = {
                "completed_modules": [
                    {
                        "title": p.module.title if p.module else "Unknown",
                        "score": p.quiz_score or 0,
                        "assignment_completed": p.assignment_completed
                    }
                    for p in progress_items if p.module is not None
                ]
            }
        
        # Generate the module content
        module_data = await content_generation_service.generate_module(
            user_prompt=request.prompt,
            user_background=request.background_knowledge,
            user_progress=user_progress
        )
        
        # Create new module in the database
        module = LearningModule(
            user_id=current_user.id,  # Set the user_id from the authenticated user
            title=module_data["title"],
            description=module_data["description"],
            content=module_data["content"],
            video_links=module_data["video_links"],
            assignment_latex=module_data["assignment_latex"],
            quiz_data=module_data["quiz_data"],
            difficulty_level=module_data.get("difficulty_level", 1),
            prerequisites=module_data.get("prerequisites", "[]")
        )
        
        # Save to database
        session.add(module)
        session.commit()
        session.refresh(module)
        
        # Parse quiz_data if it's a string
        quiz_questions = None
        if module.quiz_data:
            try:
                quiz_data_parsed = json.loads(module.quiz_data) if isinstance(module.quiz_data, str) else module.quiz_data
                quiz_questions = quiz_data_parsed.get("questions", [])
            except (json.JSONDecodeError, AttributeError):
                quiz_questions = []
        
        # Map difficulty level to string
        difficulty_map = {1: "easy", 2: "medium", 3: "hard"}
        difficulty = difficulty_map.get(module.difficulty_level, "medium")
        
        # Create the module response
        module_response = ModuleResponse(
            id=module.id,
            title=module.title,
            description=module.description,
            content=module.content,
            video_links=module.video_links,
            assignment_url=f"/api/v1/modules/{module.id}/assignment",
            quiz_data=module.quiz_data,
            quiz_questions=quiz_questions,
            difficulty=difficulty,
            duration=30,  # Default duration
            created_at=module.created_at.isoformat() if module.created_at else None
        )
        
        # Return the expected format for frontend
        return {
            "success": True,
            "module_id": module.id,
            "module": module_response.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating module: {str(e)}"
        )


@router.get("/{module_id}")
async def get_module(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a learning module by ID.
    
    Args:
        module_id: ID of the module to retrieve
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        The learning module
    """
    module = session.get(LearningModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    return ModuleResponse(
        id=module.id,
        title=module.title,
        description=module.description,
        content=module.content,
        video_links=module.video_links,
        assignment_url=f"/api/v1/modules/{module.id}/assignment",
        quiz_data=module.quiz_data
    )


@router.get("/")
async def get_user_modules(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all modules for the current user"""
    statement = select(LearningModule).where(LearningModule.user_id == current_user.id)
    modules = session.exec(statement).all()
    
    results = []
    for module in modules:
        # Parse JSON content if it exists
        try:
            content_data = json.loads(module.content) if module.content else {}
        except:
            content_data = {"content": module.content or ""}
        
        try:
            video_links = json.loads(module.video_links) if module.video_links else []
        except:
            video_links = []
            
        try:
            quiz_data = json.loads(module.quiz_data) if isinstance(module.quiz_data, str) else module.quiz_data
            quiz_questions = quiz_data.get("questions", []) if quiz_data else []
        except:
            quiz_data = {}
            quiz_questions = []
        
        # Map difficulty level to string
        difficulty_map = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}
        difficulty = difficulty_map.get(module.difficulty_level, "Medium")
        
        results.append({
            "id": module.id,
            "title": module.title,
            "description": module.description or content_data.get("description", ""),
            "content": content_data.get("content", module.content or ""),
            "video_links": video_links,
            "assignment_url": f"/api/v1/modules/{module.id}/assignment",
            "quiz_data": quiz_data,
            "difficulty": difficulty.lower(),
            "duration": 30,  # Default duration
            "quiz_questions": quiz_questions,
            "assignment_latex": module.assignment_latex,
            "status": "active",
            "created_at": module.created_at.isoformat() if module.created_at else None
        })
    
    return results


@router.delete("/{module_id}")
async def delete_module(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a module (only if it belongs to the current user)"""
    module = session.get(LearningModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    # Check if the module belongs to the current user
    if module.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own modules"
        )
    
    session.delete(module)
    session.commit()
    
    return {"success": True, "message": f"Module '{module.title}' has been deleted"}


@router.post("/{module_id}/quiz/submit")
async def submit_quiz(
    module_id: int,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit quiz answers and get results"""
    module = session.get(LearningModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    try:
        import json
        quiz_data = json.loads(module.quiz_data) if module.quiz_data else {"questions": []}
        questions = quiz_data.get("questions", [])
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No quiz questions found for this module"
            )
        
        correct_answers = 0
        total_questions = len(questions)
        feedback = []
        
        for i, question in enumerate(questions):
            question_id = str(i)
            user_answer = submission.answers.get(question_id)
            correct_answer = question.get("correct_answer")
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_answers += 1
            
            feedback.append({
                "question_id": question_id,
                "question": question.get("question"),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Save user progress
        progress = UserProgress(
            user_id=current_user.id,
            module_id=module_id,
            quiz_score=score,
            quiz_completed=True
        )
        session.add(progress)
        session.commit()
        
        return QuizResult(
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            feedback=feedback
        )
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid quiz data format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing quiz submission: {str(e)}"
        )


@router.get("/{module_id}/assignment")
async def download_assignment(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Download assignment for a module"""
    from fastapi.responses import Response
    
    module = session.get(LearningModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    if not module.assignment_latex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assignment available for this module"
        )
    
    # For now, return the LaTeX content as text
    # In production, you might want to compile this to PDF
    return Response(
        content=module.assignment_latex,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=assignment_{module_id}.tex"}
    )
