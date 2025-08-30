from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.db.session import engine
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.modules import router as modules_router
from app.api.v1.quizzes import router as quizzes_router
from app.api.v1.assignments import router as assignments_router
from app.api.v1.learning_paths import router as learning_paths_router
from app.api.v1.enhanced_modules import router as enhanced_modules_router
from app.api.v1.enhanced_chat import router as enhanced_chat_router
from app.api.v1.health import router as health_router

app = FastAPI(
	title="GyanForge API",
	description="Backend API for GyanForge adaptive learning platform with AI-powered content generation",
	version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
	# Create database tables
	SQLModel.metadata.create_all(engine)

# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(modules_router)
app.include_router(enhanced_modules_router)
app.include_router(quizzes_router)
app.include_router(assignments_router)
app.include_router(learning_paths_router)
app.include_router(enhanced_chat_router)
app.include_router(health_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to GyanForge API v2.0 - AI-Powered Learning Platform",
        "features": [
            "AI-generated educational content",
            "YouTube video recommendations", 
            "Adaptive quizzes with personalized feedback",
            "Context-aware chat assistant",
            "PDF notes and assignments generation",
            "Learning progress analytics"
        ],
        "docs": "/docs",
        "version": "2.0.0"
    }
