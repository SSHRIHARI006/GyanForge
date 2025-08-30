from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
import json
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.models import User, LearningModule
from app.services.content_service import ContentGenerationService
from app.services.quiz_service import QuizService
from app.services.youtube_service import YouTubeService
from app.utils.pdf_generator import PDFGenerator
from app.core.security import get_current_user

router = APIRouter()

# Initialize services
content_service = ContentGenerationService()
youtube_service = YouTubeService()
quiz_service = QuizService()
pdf_generator = PDFGenerator()

class ModuleRequest(BaseModel):
    topic: str
    difficulty: str = "Beginner"

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[int]

@router.post("/modules/generate")
async def generate_comprehensive_module(
    request: ModuleRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Generate a comprehensive learning module with videos, notes, and assignments"""
    try:
        # Generate comprehensive module
        module_data = await content_service.generate_module(
            user_prompt=request.topic,
            user_background=f"Difficulty: {request.difficulty}"
        )
        
        # Enhance module data if AI generation failed
        if "error" in module_data or not module_data.get("content"):
            module_data = {
                "title": f"{request.topic} - {request.difficulty} Level",
                "description": f"Learn the fundamentals of {request.topic} with this comprehensive {request.difficulty.lower()}-level module.",
                "content": f"""# {request.topic} - Getting Started

## Overview
Welcome to your {request.topic} learning module! This comprehensive guide will take you through the essential concepts and practical applications.

## Key Learning Objectives
- Understand the core concepts of {request.topic}
- Apply fundamental principles in practical scenarios  
- Build confidence through hands-on examples
- Master {request.difficulty.lower()}-level techniques

## What You'll Learn
This module covers the essential topics you need to know about {request.topic}. We'll start with the basics and gradually build up to more advanced concepts.

## Getting Started
Ready to begin your learning journey? Let's dive into the fascinating world of {request.topic}!

---
*Note: This is a foundational module. For more detailed AI-generated content, please check your API configuration.*""",
                "video_links": json.dumps([{
                    "title": f"Introduction to {request.topic}",
                    "url": f"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                    "duration": "15:30"
                }]),
                "assignment_latex": f"\\textbf{{Practice Exercise:}} Research and summarize three key concepts related to {request.topic}. Write a brief explanation for each concept and provide a real-world example.",
                "quiz_data": json.dumps({
                    "questions": [
                        {
                            "question": f"What is the primary focus of this {request.topic} module?",
                            "type": "multiple_choice",
                            "options": [
                                "Learning fundamentals",
                                "Advanced techniques only", 
                                "Quick overview",
                                "Professional certification"
                            ],
                            "correct_answer": "Learning fundamentals",
                            "explanation": "This module focuses on building a strong foundation in the topic."
                        },
                        {
                            "question": f"What difficulty level is this {request.topic} module designed for?",
                            "type": "multiple_choice", 
                            "options": ["Beginner", "Intermediate", "Advanced", "Expert"],
                            "correct_answer": request.difficulty,
                            "explanation": f"This module is specifically designed for {request.difficulty.lower()}-level learners."
                        }
                    ]
                }),
                "difficulty_level": difficulty_map.get(request.difficulty, 1),
                "prerequisites": json.dumps(["Basic computer literacy", "Willingness to learn"])
            }
        
        # Save module to database
        difficulty_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
        
        # Use enhanced content if available, otherwise the AI-generated content
        final_module_data = module_data if not ("error" in module_data) else {
            "title": f"{request.topic} - {request.difficulty} Level",
            "description": f"Learn the fundamentals of {request.topic}.",
            "content": f"Introduction to {request.topic} concepts and practices."
        }
        
        module = LearningModule(
            user_id=current_user.id,
            title=final_module_data.get("title", request.topic),
            description=final_module_data.get("description", ""),
            content=json.dumps(final_module_data),
            video_links=final_module_data.get("video_links"),
            assignment_latex=final_module_data.get("assignment_latex"),
            quiz_data=final_module_data.get("quiz_data"),
            difficulty_level=difficulty_map.get(request.difficulty, 1)
        )
        session.add(module)
        session.commit()
        session.refresh(module)
        
        return {
            "success": True,
            "module_id": module.id,
            "module": module_data
        }
        
    except Exception as e:
        print(f"Error generating module: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate module")

@router.get("/modules/{module_id}")
async def get_module(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific module by ID"""
    module = session.get(Module, module_id)
    
    if not module or module.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "success": True,
        "module": module
    }

@router.get("/modules")
async def get_user_modules(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 10
):
    """Get all modules for the current user"""
    statement = select(Module).where(Module.user_id == current_user.id).offset(skip).limit(limit)
    modules = session.exec(statement).all()
    
    return {
        "success": True,
        "modules": modules,
        "total": len(modules)
    }

@router.get("/videos/recommend/{topic}")
async def get_recommended_videos(topic: str):
    """Get recommended YouTube videos for a topic"""
    try:
        videos = youtube_service.get_recommended_videos(topic)
        
        return {
            "success": True,
            "topic": topic,
            "videos": videos,
            "count": len(videos)
        }
        
    except Exception as e:
        print(f"Error getting video recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video recommendations")

@router.post("/quiz/generate")
async def generate_adaptive_quiz(
    request: ModuleRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate an adaptive quiz for a topic"""
    try:
        quiz = quiz_service.generate_adaptive_quiz(
            topic=request.topic,
            user_id=current_user.id,
            difficulty=request.difficulty
        )
        
        return {
            "success": True,
            "quiz": quiz
        }
        
    except Exception as e:
        print(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quiz")

@router.post("/quiz/submit")
async def submit_quiz(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user)
):
    """Submit quiz answers and get evaluation"""
    try:
        evaluation = quiz_service.evaluate_quiz_submission(
            quiz_id=submission.quiz_id,
            user_answers=submission.answers,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "evaluation": evaluation
        }
        
    except Exception as e:
        print(f"Error evaluating quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate quiz")

@router.get("/modules/{module_id}/notes/download")
async def download_notes(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Download notes as PDF"""
    try:
        module = session.get(Module, module_id)
        
        if not module or module.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Extract notes from module content
        notes = module.content.get('notes', {})
        
        if not notes:
            raise HTTPException(status_code=404, detail="No notes found for this module")
        
        # Generate PDF
        pdf_content = pdf_generator.generate_notes_pdf(notes, module.title)
        
        return {
            "success": True,
            "pdf_url": f"/api/v1/downloads/notes_{module_id}.pdf",
            "filename": f"notes_{module.title.replace(' ', '_')}.pdf"
        }
        
    except Exception as e:
        print(f"Error generating notes PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate notes PDF")

@router.get("/modules/{module_id}/assignments/download")
async def download_assignments(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Download assignments as PDF"""
    try:
        module = session.get(Module, module_id)
        
        if not module or module.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Extract assignments from module content
        assignments = module.content.get('assignments', [])
        
        if not assignments:
            raise HTTPException(status_code=404, detail="No assignments found for this module")
        
        # Generate PDF
        pdf_content = pdf_generator.generate_assignments_pdf(assignments, module.title)
        
        return {
            "success": True,
            "pdf_url": f"/api/v1/downloads/assignments_{module_id}.pdf",
            "filename": f"assignments_{module.title.replace(' ', '_')}.pdf"
        }
        
    except Exception as e:
        print(f"Error generating assignments PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate assignments PDF")

@router.delete("/modules/{module_id}")
async def delete_module(
    module_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a module"""
    module = session.get(Module, module_id)
    
    if not module or module.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Module not found")
    
    session.delete(module)
    session.commit()
    
    return {
        "success": True,
        "message": "Module deleted successfully"
    }

@router.get("/analytics/learning-progress")
async def get_learning_progress(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get user's learning progress analytics"""
    try:
        # Get all user modules
        modules = session.exec(
            select(Module).where(Module.user_id == current_user.id)
        ).all()
        
        # Calculate analytics
        total_modules = len(modules)
        topics_covered = list(set([module.title for module in modules]))
        difficulties = [module.difficulty for module in modules]
        
        difficulty_distribution = {
            "Beginner": difficulties.count("Beginner"),
            "Intermediate": difficulties.count("Intermediate"),
            "Advanced": difficulties.count("Advanced")
        }
        
        # Learning streak (simplified - count of modules)
        learning_streak = total_modules
        
        return {
            "success": True,
            "analytics": {
                "total_modules": total_modules,
                "topics_covered": topics_covered,
                "difficulty_distribution": difficulty_distribution,
                "learning_streak": learning_streak,
                "recent_activity": [
                    {
                        "module": module.title,
                        "difficulty": module.difficulty,
                        "created_at": module.created_at
                    } for module in modules[-5:]  # Last 5 modules
                ]
            }
        }
        
    except Exception as e:
        print(f"Error getting learning progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning progress")

@router.get("/recommendations/next-topics")
async def get_next_topic_recommendations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get personalized next topic recommendations"""
    try:
        # Get user's completed modules
        modules = session.exec(
            select(Module).where(Module.user_id == current_user.id)
        ).all()
        
        completed_topics = [module.title for module in modules]
        
        # Generate recommendations based on completed topics
        recommendations = []
        
        # Simple recommendation logic (can be enhanced with AI)
        if any("python" in topic.lower() for topic in completed_topics):
            if not any("web" in topic.lower() for topic in completed_topics):
                recommendations.append({
                    "topic": "Web Development with Python",
                    "difficulty": "Intermediate",
                    "reason": "Build on your Python knowledge"
                })
        
        if any("javascript" in topic.lower() for topic in completed_topics):
            if not any("react" in topic.lower() for topic in completed_topics):
                recommendations.append({
                    "topic": "React.js Fundamentals",
                    "difficulty": "Intermediate", 
                    "reason": "Advance your JavaScript skills"
                })
        
        # Default recommendations for new users
        if not completed_topics:
            recommendations.extend([
                {
                    "topic": "Introduction to Programming",
                    "difficulty": "Beginner",
                    "reason": "Perfect starting point"
                },
                {
                    "topic": "Python Basics",
                    "difficulty": "Beginner",
                    "reason": "Popular and beginner-friendly"
                }
            ])
        
        return {
            "success": True,
            "recommendations": recommendations[:5]  # Top 5 recommendations
        }
        
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")
