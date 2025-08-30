import json
import logging
from typing import Dict, List, Optional, Any
from sqlmodel import Session

logger = logging.getLogger(__name__)

class SimpleChatService:
    """Simple chat service without AI dependencies"""
    
    def __init__(self):
        self.responses = {
            "hello": "Hello! I'm here to help you with your learning journey.",
            "help": "I can help you with data structures, algorithms, and programming concepts.",
            "heap": "A heap is a complete binary tree where each parent node is greater (max-heap) or smaller (min-heap) than its children.",
            "stack": "A stack is a Last-In-First-Out (LIFO) data structure. Think of it like a stack of plates.",
            "queue": "A queue is a First-In-First-Out (FIFO) data structure. Think of it like a line at a store.",
            "tree": "A tree is a hierarchical data structure with nodes connected by edges, starting from a root node.",
            "graph": "A graph is a collection of nodes (vertices) connected by edges. It can be directed or undirected.",
            "algorithm": "An algorithm is a step-by-step procedure to solve a problem.",
            "programming": "Programming is the process of creating instructions for computers to follow."
        }
    
    async def get_response(self, message: str, user_id: str = None, context: Dict = None) -> Dict[str, Any]:
        """Generate a simple response based on keywords"""
        try:
            message_lower = message.lower()
            
            # Simple keyword matching
            for keyword, response in self.responses.items():
                if keyword in message_lower:
                    return {
                        "response": response,
                        "confidence": 0.8,
                        "source": "keyword_match"
                    }
            
            # Default response
            return {
                "response": "That's an interesting question! I recommend checking out our learning modules for more detailed information on data structures and algorithms.",
                "confidence": 0.5,
                "source": "default"
            }
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return {
                "response": "I'm having trouble understanding your question right now. Please try again.",
                "confidence": 0.1,
                "source": "error"
            }
    
    async def process_chat_message(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process a chat message and return response"""
        response_data = await self.get_response(message, user_id)
        
        return {
            "message": message,
            "response": response_data["response"],
            "metadata": {
                "confidence": response_data["confidence"],
                "source": response_data["source"],
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
