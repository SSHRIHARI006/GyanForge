from typing import Dict, List, Optional, Any, Tuple
import json
import logging
import google.generativeai as genai
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlmodel import Session, select

from app.core.config import settings
from app.models.models import User, UserProgress, LearningModule, UserLearningGoal

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


class LearningPathService:
    """
    An AI agent that determines the optimal learning path for a user based on their:
    1. Quiz results
    2. Learning history
    3. Learning goals
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
        self.tools = self._create_tools()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the LangChain agent."""
        return [
            Tool(
                name="get_user_progress",
                description=(
                    "Get a user's learning history and progress. "
                    "Input should be a user_id (integer)."
                ),
                func=self._get_user_progress_tool
            ),
            Tool(
                name="get_knowledge_graph",
                description=(
                    "Get prerequisite and next topics for a given subject. "
                    "Input should be a topic name (string)."
                ),
                func=self._get_knowledge_graph_tool
            ),
            Tool(
                name="get_module_details",
                description=(
                    "Get detailed information about a learning module. "
                    "Input should be a module_id (integer)."
                ),
                func=self._get_module_details_tool
            ),
        ]
        
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent."""
        prompt = PromptTemplate(
            template="""You are GyanForge's Learning Path Engine, an AI tutor responsible for guiding students through personalized learning journeys.

Your goal is to determine what topic a student should learn next based on their progress, quiz scores, and learning goals.

Use your tools to:
1. Get the student's learning history and quiz scores
2. Understand the knowledge graph of topics (prerequisites and next steps)
3. Analyze module details if needed

Here are some guidelines:
- If a student scored below 70% on a topic, they should review it or try a simpler prerequisite
- If a student scored above 90%, they're ready for more advanced material
- Always check prerequisites before recommending advanced topics
- Consider the student's learning goals and background

{chat_history}
""",
            input_variables=["chat_history"],
        )
        
        # Create the agent using ReAct framework
        agent = create_react_agent(self.model, self.tools, prompt)
        
        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _get_user_progress_tool(self, user_id: str) -> str:
        """
        Tool that fetches a user's learning history and progress.
        
        Args:
            user_id: The ID of the user to get progress for
            
        Returns:
            JSON string with user's learning history
        """
        try:
            user_id_int = int(user_id.strip())
            
            # Query the user
            user = self.db_session.get(User, user_id_int)
            if not user:
                return json.dumps({"error": f"User with ID {user_id_int} not found"})
            
            # Get user's progress
            progress_items = self.db_session.exec(
                select(UserProgress)
                .where(UserProgress.user_id == user_id_int)
            ).all()
            
            # Get user's learning goals
            goals = self.db_session.exec(
                select(UserLearningGoal)
                .where(UserLearningGoal.user_id == user_id_int)
            ).all()
            
            # Format the response
            result = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": getattr(user, "full_name", None),
                },
                "progress": [],
                "goals": []
            }
            
            # Add progress items
            for p in progress_items:
                module = self.db_session.get(LearningModule, p.module_id)
                if module:
                    result["progress"].append({
                        "module_id": p.module_id,
                        "module_title": module.title,
                        "quiz_score": p.quiz_score,
                        "quiz_completed_at": p.quiz_completed_at.isoformat() if p.quiz_completed_at else None,
                        "assignment_completed": p.assignment_completed,
                        "assignment_completed_at": p.assignment_completed_at.isoformat() if p.assignment_completed_at else None,
                        "notes": p.notes,
                        "created_at": p.created_at.isoformat()
                    })
            
            # Add goals
            for g in goals:
                result["goals"].append({
                    "goal_description": g.goal_description,
                    "topic_area": g.topic_area,
                    "background_knowledge": g.background_knowledge,
                    "target_completion_date": g.target_completion_date.isoformat() if g.target_completion_date else None,
                    "created_at": g.created_at.isoformat()
                })
            
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": f"Error getting user progress: {str(e)}"})
    
    def _get_knowledge_graph_tool(self, topic: str) -> str:
        """
        Tool that returns prerequisite and next topics for a given subject.
        
        Args:
            topic: The topic to get knowledge graph for
            
        Returns:
            JSON string with prerequisites and next topics
        """
        # In a full implementation, this would query a knowledge graph database
        # For now, we'll use a simple hardcoded implementation for common topics
        
        topic = topic.strip().lower()
        
        # Programming knowledge graph (example)
        knowledge_graph = {
            "python basics": {
                "prerequisites": ["computer basics"],
                "next_topics": ["python data structures", "python functions", "python loops and conditionals"]
            },
            "python data structures": {
                "prerequisites": ["python basics"],
                "next_topics": ["python advanced data structures", "python algorithms"]
            },
            "python functions": {
                "prerequisites": ["python basics"],
                "next_topics": ["python lambda functions", "python modules"]
            },
            "linked list": {
                "prerequisites": ["programming basics", "arrays"],
                "next_topics": ["stacks", "queues", "trees"]
            },
            "arrays": {
                "prerequisites": ["programming basics"],
                "next_topics": ["linked list", "searching algorithms", "sorting algorithms"]
            }
        }
        
        # Try to find the topic in our knowledge graph
        for known_topic, details in knowledge_graph.items():
            if topic in known_topic or known_topic in topic:
                return json.dumps({
                    "topic": known_topic,
                    "prerequisites": details["prerequisites"],
                    "next_topics": details["next_topics"]
                })
        
        # If no match is found, return a default response
        return json.dumps({
            "topic": topic,
            "prerequisites": [],
            "next_topics": [],
            "message": "No detailed knowledge graph available for this topic"
        })
        
    def _get_module_details_tool(self, module_id: str) -> str:
        """
        Tool that fetches details about a specific learning module.
        
        Args:
            module_id: The ID of the module to get details for
            
        Returns:
            JSON string with module details
        """
        try:
            module_id_int = int(module_id.strip())
            
            # Query the module
            module = self.db_session.get(LearningModule, module_id_int)
            if not module:
                return json.dumps({"error": f"Module with ID {module_id_int} not found"})
            
            # Get related progress entries to see how users have performed on this module
            progress_items = self.db_session.exec(
                select(UserProgress)
                .where(UserProgress.module_id == module_id_int)
            ).all()
            
            # Calculate statistics
            completion_rate = 0
            avg_quiz_score = 0
            completion_count = 0
            
            if progress_items:
                # Count completed quizzes
                quiz_completed = [p for p in progress_items if p.quiz_completed_at is not None]
                completion_count = len(quiz_completed)
                completion_rate = completion_count / len(progress_items) if progress_items else 0
                
                # Calculate average quiz score
                if quiz_completed:
                    avg_quiz_score = sum(p.quiz_score or 0 for p in quiz_completed) / len(quiz_completed)
            
            # Format the response
            content = module.content
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass  # Keep as string if not valid JSON
            
            result = {
                "id": module.id,
                "title": module.title,
                "subject": module.subject,
                "difficulty_level": module.difficulty_level,
                "content_structure": {
                    "notes": content.get("notes", {}) if isinstance(content, dict) else {},
                    "videos": content.get("videos", []) if isinstance(content, dict) else [],
                    "has_quiz": bool(content.get("quiz", [])) if isinstance(content, dict) else False,
                    "has_assignment": bool(content.get("assignment", {})) if isinstance(content, dict) else False
                },
                "stats": {
                    "completion_rate": completion_rate,
                    "avg_quiz_score": avg_quiz_score,
                    "completion_count": completion_count
                },
                "created_at": module.created_at.isoformat()
            }
            
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": f"Error getting module details: {str(e)}"})
            
    def generate_learning_path(self, user_id: int, topic: str, goal_description: str) -> dict:
        """
        Generate a personalized learning path for the user based on their goals and progress.
        
        Args:
            user_id: The user ID
            topic: The general topic or subject area
            goal_description: The user's learning goal
            
        Returns:
            A dictionary containing the recommended learning path
        """
        try:
            # Create the agent with the tools
            agent = self._create_agent()
            
            # Format the prompt for the agent
            prompt = f"""
            Generate a personalized learning path for a user with the following information:
            
            USER ID: {user_id}
            TOPIC AREA: {topic}
            LEARNING GOAL: {goal_description}
            
            First, analyze the user's current progress using the get_user_progress tool.
            Then, examine the knowledge graph for the requested topic using the get_knowledge_graph tool.
            Based on the user's progress and the knowledge graph, create a step-by-step learning path.
            
            For each step in the learning path:
            1. If there's an existing module that fits the step, include its details from get_module_details
            2. If no suitable module exists, suggest a new module to be created
            
            Your response should be in JSON format with the following structure:
            {{
                "learning_path": [
                    {{
                        "step": 1,
                        "topic": "specific topic",
                        "module_id": 123,  // if existing module
                        "module_title": "title",  // if existing module
                        "create_new": false,  // true if new module needed
                        "module_description": "description"  // for new modules
                    }},
                    // More steps...
                ],
                "estimated_completion_time": "2 weeks",
                "difficulty_level": "intermediate",
                "prerequisites_met": true/false,
                "reasoning": "explanation of the recommended path"
            }}
            """
            
            # Execute the agent
            result = agent.invoke({"input": prompt})
            
            # Extract the learning path from the agent's response
            try:
                # Try to parse the agent's output as JSON
                if isinstance(result, dict) and "output" in result:
                    content = result["output"]
                    # Look for JSON content in the output
                    json_start = content.find('{')
                    json_end = content.rfind('}')
                    if json_start >= 0 and json_end >= 0:
                        json_str = content[json_start:json_end+1]
                        learning_path = json.loads(json_str)
                        return learning_path
                
                # If parsing fails, return the raw output
                return {"raw_output": str(result), "error": "Failed to parse structured learning path"}
            except json.JSONDecodeError:
                return {"raw_output": str(result), "error": "Failed to parse structured learning path"}
            except Exception as e:
                return {"error": f"Error processing agent output: {str(e)}", "raw_output": str(result)}
                
        except Exception as e:
            logging.error(f"Error generating learning path: {str(e)}")
            return {"error": f"Error generating learning path: {str(e)}"}
