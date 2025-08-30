from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class LearningPathRequest(BaseModel):
    """Schema for requesting a personalized learning path."""
    topic_area: str = Field(..., description="The general topic or subject area")
    goal_description: str = Field(..., description="The user's learning goal description")
    background_knowledge: Optional[str] = Field(None, description="User's existing knowledge in the topic area")
    target_completion_date: Optional[datetime] = Field(None, description="Target date for completing the learning goal")


class LearningPathStepBase(BaseModel):
    """Base schema for a step in a learning path."""
    step: int
    topic: str


class ExistingModuleStep(LearningPathStepBase):
    """Schema for a learning path step with an existing module."""
    module_id: int
    module_title: str
    create_new: bool = False


class NewModuleStep(LearningPathStepBase):
    """Schema for a learning path step that requires creating a new module."""
    create_new: bool = True
    module_description: str


class LearningPathResponse(BaseModel):
    """Schema for the response with a personalized learning path."""
    learning_path: List[Dict[str, Any]]
    estimated_completion_time: str
    difficulty_level: str
    prerequisites_met: bool
    reasoning: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
