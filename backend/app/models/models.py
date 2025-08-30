from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    progress: List["UserProgress"] = Relationship(back_populates="user")
    goals: List["UserLearningGoal"] = Relationship(back_populates="user")
    modules: List["LearningModule"] = Relationship(back_populates="user")

class LearningModule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    content: Optional[str] = None  # JSON or markdown
    video_links: Optional[str] = None  # JSON stringified list of YouTube videos
    assignment_latex: Optional[str] = None  # LaTeX source for the assignment
    assignment_pdf_path: Optional[str] = None  # Path to generated PDF on disk
    quiz_data: Optional[str] = None  # JSON stringified quiz questions and answers
    difficulty_level: int = 1  # 1-5 scale
    prerequisites: Optional[str] = None  # JSON stringified list of prerequisite concepts
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="modules")
    progress: List["UserProgress"] = Relationship(back_populates="module")

class UserProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    module_id: int = Field(foreign_key="learningmodule.id")
    quiz_score: Optional[float] = None
    quiz_completed_at: Optional[datetime] = None
    assignment_completed: bool = Field(default=False)
    assignment_completed_at: Optional[datetime] = None
    notes: Optional[str] = None  # Any additional notes or feedback
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="progress")
    module: "LearningModule" = Relationship(back_populates="progress")

class UserLearningGoal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    goal_description: str
    topic_area: str
    background_knowledge: Optional[str] = None  # User's self-reported background
    target_completion_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="goals")
