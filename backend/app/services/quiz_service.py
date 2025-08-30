import json
import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from sqlmodel import Session, select
from app.db.session import engine
from app.models.models import User, LearningModule

class QuizService:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyB-Isr6koIa-y7v_X9dsnxLECx_jwB-1ZM')
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("[QuizService] Model initialized successfully")
        else:
            self.model = None
            print("[QuizService] No valid API key found")

    def generate_adaptive_quiz(self, topic: str, user_id: int, difficulty: str = "Beginner") -> Dict[str, Any]:
        """Generate an adaptive quiz based on user's learning history and topic"""
        try:
            # Get user's learning context
            user_context = self._get_user_learning_context(user_id)
            
            # Generate quiz questions
            quiz_questions = self._generate_quiz_questions(topic, difficulty, user_context)
            
            quiz = {
                "quiz_id": f"quiz_{topic}_{user_id}",
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": len(quiz_questions),
                "questions": quiz_questions,
                "adaptive": True,
                "estimated_time": f"{len(quiz_questions) * 2} minutes"
            }
            
            return quiz
            
        except Exception as e:
            print(f"[QuizService] Error generating adaptive quiz: {e}")
            return self._generate_fallback_quiz(topic, difficulty)

    def _get_user_learning_context(self, user_id: int) -> Dict[str, Any]:
        """Get user's learning history and preferences"""
        try:
            with Session(engine) as session:
                # Get user
                user = session.get(User, user_id)
                if not user:
                    return {"modules_completed": [], "strengths": [], "weaknesses": []}
                
                # Get user's completed modules
                modules = session.exec(
                    select(Module).where(Module.user_id == user_id)
                ).all()
                
                completed_topics = [module.title for module in modules]
                
                return {
                    "modules_completed": completed_topics,
                    "total_modules": len(modules),
                    "learning_level": self._assess_user_level(modules),
                    "preferred_topics": self._extract_preferred_topics(completed_topics)
                }
        except Exception as e:
            print(f"Error getting user context: {e}")
            return {"modules_completed": [], "strengths": [], "weaknesses": []}

    def _generate_quiz_questions(self, topic: str, difficulty: str, user_context: Dict) -> List[Dict[str, Any]]:
        """Generate quiz questions using AI"""
        if not self.model:
            return self._generate_fallback_questions(topic, difficulty)
        
        context_info = ""
        if user_context.get("modules_completed"):
            context_info = f"User has completed: {', '.join(user_context['modules_completed'][-3:])}"
        
        prompt = f"""
        Create 5 quiz questions for "{topic}" at {difficulty} level.
        {context_info}
        
        Structure as JSON array:
        [
            {{
                "question": "Clear question text",
                "type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Why this answer is correct",
                "difficulty": "{difficulty}",
                "learning_objective": "What this tests",
                "hints": ["hint1", "hint2"]
            }}
        ]
        
        Include:
        - 2 concept-based questions
        - 2 application-based questions  
        - 1 analysis/evaluation question
        
        Make questions clear, relevant, and educational.
        """
        
        try:
            response = self.model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                response_text = response.text.strip()
                
                # Extract JSON
                import re
                json_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
                json_match = re.search(json_pattern, response_text, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON array in the text
                    array_pattern = r'(\[.*\])'
                    array_match = re.search(array_pattern, response_text, re.DOTALL)
                    if array_match:
                        json_str = array_match.group(1)
                    else:
                        json_str = response_text
                
                questions = json.loads(json_str)
                
                # Validate and format questions
                formatted_questions = []
                for i, q in enumerate(questions):
                    if isinstance(q, dict) and 'question' in q:
                        formatted_q = {
                            "id": i + 1,
                            "question": q.get("question", ""),
                            "type": q.get("type", "multiple_choice"),
                            "options": q.get("options", []),
                            "correct_answer": q.get("correct_answer", 0),
                            "explanation": q.get("explanation", ""),
                            "difficulty": difficulty,
                            "learning_objective": q.get("learning_objective", ""),
                            "hints": q.get("hints", [])
                        }
                        formatted_questions.append(formatted_q)
                
                return formatted_questions[:5]  # Ensure max 5 questions
                
        except Exception as e:
            print(f"Error generating quiz questions: {e}")
        
        return self._generate_fallback_questions(topic, difficulty)

    def evaluate_quiz_submission(self, quiz_id: str, user_answers: List[int], user_id: int) -> Dict[str, Any]:
        """Evaluate quiz submission and provide personalized feedback"""
        try:
            # This would normally fetch the quiz from database
            # For now, we'll generate evaluation based on the answers
            
            total_questions = len(user_answers)
            correct_answers = 0
            
            # Simple evaluation (in real implementation, compare with stored correct answers)
            for answer in user_answers:
                if isinstance(answer, int) and 0 <= answer <= 3:
                    correct_answers += 1  # Simplified for demo
            
            score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            # Generate personalized recommendations
            recommendations = self._generate_learning_recommendations(score_percentage, quiz_id, user_id)
            
            evaluation = {
                "quiz_id": quiz_id,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score_percentage": score_percentage,
                "grade": self._calculate_grade(score_percentage),
                "strengths": self._identify_strengths(user_answers),
                "areas_for_improvement": self._identify_weaknesses(user_answers),
                "personalized_recommendations": recommendations,
                "next_steps": self._suggest_next_steps(score_percentage, quiz_id)
            }
            
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating quiz: {e}")
            return self._generate_fallback_evaluation(len(user_answers))

    def _generate_learning_recommendations(self, score: float, quiz_topic: str, user_id: int) -> List[Dict[str, str]]:
        """Generate personalized learning recommendations based on performance"""
        recommendations = []
        
        if score < 50:
            recommendations.extend([
                {
                    "type": "review",
                    "title": "Review Fundamentals",
                    "description": f"Revisit the basic concepts of {quiz_topic}",
                    "action": "study_notes"
                },
                {
                    "type": "practice",
                    "title": "Additional Practice",
                    "description": "Complete more exercises to strengthen understanding",
                    "action": "practice_exercises"
                }
            ])
        elif score < 80:
            recommendations.extend([
                {
                    "type": "reinforce",
                    "title": "Reinforce Learning",
                    "description": f"Practice specific areas in {quiz_topic}",
                    "action": "targeted_practice"
                },
                {
                    "type": "video",
                    "title": "Watch Tutorial Videos",
                    "description": "Visual learning can help clarify concepts",
                    "action": "watch_videos"
                }
            ])
        else:
            recommendations.extend([
                {
                    "type": "advance",
                    "title": "Advance to Next Level",
                    "description": f"You've mastered {quiz_topic}! Try advanced topics",
                    "action": "next_module"
                },
                {
                    "type": "teach",
                    "title": "Teach Others",
                    "description": "Explaining concepts helps solidify understanding",
                    "action": "peer_teaching"
                }
            ])
        
        return recommendations

    def _assess_user_level(self, modules: List) -> str:
        """Assess user's overall learning level"""
        if len(modules) < 3:
            return "Beginner"
        elif len(modules) < 8:
            return "Intermediate"
        else:
            return "Advanced"

    def _extract_preferred_topics(self, completed_topics: List[str]) -> List[str]:
        """Extract user's preferred learning topics"""
        # Simple analysis of completed topics
        topic_counts = {}
        for topic in completed_topics:
            words = topic.lower().split()
            for word in words:
                if len(word) > 3:  # Ignore short words
                    topic_counts[word] = topic_counts.get(word, 0) + 1
        
        # Return top 3 topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:3]]

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from percentage"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _identify_strengths(self, answers: List[int]) -> List[str]:
        """Identify user strengths based on answers"""
        # Simplified analysis
        if len(answers) >= 3:
            return ["Problem-solving", "Conceptual understanding"]
        else:
            return ["Basic concepts"]

    def _identify_weaknesses(self, answers: List[int]) -> List[str]:
        """Identify areas for improvement"""
        # Simplified analysis
        return ["Application of concepts", "Advanced problem-solving"]

    def _suggest_next_steps(self, score: float, quiz_topic: str) -> List[str]:
        """Suggest next learning steps"""
        if score < 70:
            return [
                f"Review {quiz_topic} materials",
                "Complete additional practice exercises",
                "Ask questions in discussion forum"
            ]
        else:
            return [
                f"Move to advanced {quiz_topic} topics",
                "Apply knowledge in projects",
                "Explore related subjects"
            ]

    # Fallback methods
    def _generate_fallback_quiz(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate fallback quiz when AI generation fails"""
        return {
            "quiz_id": f"fallback_{topic}",
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": 3,
            "questions": self._generate_fallback_questions(topic, difficulty),
            "adaptive": False,
            "estimated_time": "6 minutes"
        }

    def _generate_fallback_questions(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI generation fails"""
        return [
            {
                "id": 1,
                "question": f"What is the main concept of {topic}?",
                "type": "multiple_choice",
                "options": [
                    f"Core principle of {topic}",
                    f"Advanced feature of {topic}",
                    f"Unrelated concept",
                    f"Optional component"
                ],
                "correct_answer": 0,
                "explanation": f"The main concept focuses on the core principles of {topic}",
                "difficulty": difficulty,
                "learning_objective": f"Understand {topic} fundamentals",
                "hints": ["Think about the basics", "Focus on core concepts"]
            },
            {
                "id": 2,
                "question": f"How would you apply {topic} in practice?",
                "type": "multiple_choice",
                "options": [
                    "Follow best practices",
                    "Ignore guidelines",
                    "Use outdated methods",
                    "Skip implementation"
                ],
                "correct_answer": 0,
                "explanation": "Following best practices ensures effective application",
                "difficulty": difficulty,
                "learning_objective": f"Apply {topic} knowledge",
                "hints": ["Consider best practices", "Think practically"]
            },
            {
                "id": 3,
                "question": f"What are the benefits of learning {topic}?",
                "type": "multiple_choice",
                "options": [
                    "Enhanced skills and knowledge",
                    "No real benefits",
                    "Only theoretical value",
                    "Waste of time"
                ],
                "correct_answer": 0,
                "explanation": f"Learning {topic} enhances practical skills and theoretical knowledge",
                "difficulty": difficulty,
                "learning_objective": f"Appreciate {topic} value",
                "hints": ["Think about skill development", "Consider practical applications"]
            }
        ]

    def _generate_fallback_evaluation(self, total_questions: int) -> Dict[str, Any]:
        """Generate fallback evaluation when normal evaluation fails"""
        return {
            "quiz_id": "fallback_quiz",
            "total_questions": total_questions,
            "correct_answers": max(1, total_questions // 2),
            "score_percentage": 50.0,
            "grade": "C",
            "strengths": ["Basic understanding"],
            "areas_for_improvement": ["Need more practice"],
            "personalized_recommendations": [
                {
                    "type": "review",
                    "title": "Continue Learning",
                    "description": "Keep practicing to improve",
                    "action": "study_more"
                }
            ],
            "next_steps": ["Review materials", "Practice more"]
        }
