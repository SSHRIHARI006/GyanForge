from pydantic import BaseModel
from typing import List, Optional

class GenerateModuleRequest(BaseModel):
    prompt: str
    user_id: Optional[int] = None

class Section(BaseModel):
    title: str
    content: str

class QuizItem(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class ModuleResponse(BaseModel):
    sections: List[Section]
    video_ids: List[str]
    assignment: str  # LaTeX content
    quiz: List[QuizItem]

class NextModuleResponse(BaseModel):
    next_topic: str
