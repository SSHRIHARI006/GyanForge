import json
import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from sqlmodel import Session, select
from app.db.session import engine
from app.models.models import User, LearningModule

class EnhancedChatService:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyB-Isr6koIa-y7v_X9dsnxLECx_jwB-1ZM')
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("[EnhancedChatService] Model initialized successfully")
        else:
            self.model = None
            print("[EnhancedChatService] No valid API key found")
        
        # Store conversation context per user
        self.user_contexts = {}

    def chat_with_context(self, user_id: int, message: str, current_module: Optional[str] = None) -> Dict[str, Any]:
        """Chat with learning context awareness"""
        try:
            # Get user's learning context
            learning_context = self._get_user_learning_context(user_id)
            
            # Get conversation history
            conversation_history = self.user_contexts.get(user_id, [])
            
            # Generate response with context
            response = self._generate_contextual_response(
                message, 
                learning_context, 
                conversation_history, 
                current_module
            )
            
            # Update conversation history
            self._update_conversation_history(user_id, message, response['content'])
            
            return {
                "response": response['content'],
                "suggestions": response.get('suggestions', []),
                "learning_insights": response.get('learning_insights', []),
                "recommended_actions": response.get('recommended_actions', []),
                "context_used": True
            }
            
        except Exception as e:
            print(f"[EnhancedChatService] Error in contextual chat: {e}")
            return self._generate_fallback_response(message)

    def _get_user_learning_context(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user learning context"""
        try:
            with Session(engine) as session:
                # Get user
                user = session.get(User, user_id)
                if not user:
                    return {"modules": [], "current_level": "Beginner"}
                
                # Get user's modules
                modules = session.exec(
                    select(LearningModule).where(LearningModule.user_id == user_id)
                ).all()
                
                module_topics = [module.title for module in modules]
                recent_modules = module_topics[-3:] if module_topics else []
                
                return {
                    "user_name": user.username,
                    "total_modules": len(modules),
                    "completed_topics": module_topics,
                    "recent_learning": recent_modules,
                    "learning_level": self._assess_learning_level(len(modules)),
                    "preferred_subjects": self._extract_subjects(module_topics),
                    "learning_streak": len(modules)  # Simplified
                }
        except Exception as e:
            print(f"Error getting learning context: {e}")
            return {"modules": [], "current_level": "Beginner"}

    def _generate_contextual_response(
        self, 
        message: str, 
        learning_context: Dict, 
        conversation_history: List, 
        current_module: Optional[str]
    ) -> Dict[str, Any]:
        """Generate AI response with full learning context"""
        
        if not self.model:
            return {
                "content": "I'm here to help with your learning! How can I assist you today?",
                "suggestions": ["Ask about concepts", "Request explanations", "Get study tips"],
                "learning_insights": [],
                "recommended_actions": []
            }
        
        # Build context prompt
        context_prompt = self._build_context_prompt(message, learning_context, conversation_history, current_module)
        
        try:
            response = self.model.generate_content(context_prompt)
            if response and hasattr(response, 'text'):
                response_text = response.text.strip()
                
                # Try to parse structured response
                try:
                    if response_text.startswith('{') and response_text.endswith('}'):
                        parsed_response = json.loads(response_text)
                        return parsed_response
                except:
                    pass
                
                # Generate structured response from plain text
                return self._structure_response(response_text, learning_context, current_module)
        
        except Exception as e:
            print(f"Error generating contextual response: {e}")
        
        return self._generate_fallback_response(message)

    def _build_context_prompt(
        self, 
        message: str, 
        learning_context: Dict, 
        conversation_history: List, 
        current_module: Optional[str]
    ) -> str:
        """Build comprehensive context prompt for AI"""
        
        user_name = learning_context.get('user_name', 'Student')
        recent_learning = learning_context.get('recent_learning', [])
        learning_level = learning_context.get('learning_level', 'Beginner')
        total_modules = learning_context.get('total_modules', 0)
        preferred_subjects = learning_context.get('preferred_subjects', [])
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            recent_convo = conversation_history[-4:]  # Last 4 exchanges for better context
            conversation_context = "Previous conversation context:\n"
            for i, exchange in enumerate(recent_convo):
                conversation_context += f"Exchange {i+1}:\n"
                conversation_context += f"  Student: {exchange['user']}\n"
                conversation_context += f"  Assistant: {exchange['assistant']}\n"
        
        # Build learning context
        learning_context_str = f"""
        === STUDENT PROFILE ===
        Name: {user_name}
        Learning Level: {learning_level}
        Total Modules Completed: {total_modules}
        Recent Learning Topics: {', '.join(recent_learning) if recent_learning else 'Getting started'}
        Preferred Subjects: {', '.join(preferred_subjects) if preferred_subjects else 'Exploring various topics'}
        Current Active Module: {current_module or 'Not currently in a specific module'}
        Learning Streak: {total_modules} modules completed
        """
        
        prompt = f"""You are **GyanForge AI**, an advanced educational assistant and learning companion. Your role is to provide personalized, engaging, and pedagogically sound responses that enhance the student's learning journey.

        {learning_context_str}
        
        {conversation_context}
        
        **Current Student Question/Message**: "{message}"
        
        === YOUR CORE RESPONSIBILITIES ===
        1. **Personalized Learning**: Tailor responses based on the student's level, history, and current context
        2. **Educational Excellence**: Provide accurate, comprehensive, and well-structured explanations
        3. **Socratic Method**: Use guided questioning to help students discover answers themselves
        4. **Progressive Learning**: Build upon their existing knowledge and gently introduce new concepts
        5. **Motivation & Encouragement**: Maintain a supportive, encouraging tone that builds confidence
        6. **Practical Application**: Connect theoretical concepts to real-world applications and examples
        
        === RESPONSE GUIDELINES ===
        - **Adaptive Communication**: Match your language complexity to their learning level
        - **Context Awareness**: Reference their previous learning and current module when relevant
        - **Multimodal Teaching**: Suggest different learning approaches (visual, auditory, kinesthetic)
        - **Error-Friendly Learning**: If they have misconceptions, correct gently with explanations
        - **Next Steps**: Always suggest logical next learning steps or practice opportunities
        - **Curiosity Stimulation**: Ask thought-provoking questions to deepen understanding
        
        === RESPONSE STRUCTURE (when applicable) ===
        Try to structure complex responses with:
        1. **Direct Answer**: Address their immediate question clearly
        2. **Context Connection**: Relate to their learning history or current module
        3. **Deeper Insight**: Provide additional relevant information or perspective
        4. **Practical Example**: Include a concrete, relatable example
        5. **Learning Extension**: Suggest related concepts or next steps
        
        === PREFERRED RESPONSE FORMAT ===
        If possible, respond in this JSON structure (otherwise use well-formatted text):
        {{
            "content": "Your comprehensive, educational response tailored to their level and context",
            "suggestions": ["Specific follow-up question 1", "Practice exercise suggestion", "Related concept to explore"],
            "learning_insights": ["Key insight about their learning pattern", "Strength they're demonstrating"],
            "recommended_actions": ["Immediate next step", "Practice recommendation", "Resource suggestion"]
        }}
        
        === SPECIAL CONSIDERATIONS ===
        - If they're struggling: Offer simpler explanations and break concepts down further
        - If they're advanced: Provide more challenging examples and connections
        - If they're curious about tangents: Acknowledge interest but gently guide back to learning objectives
        - If they ask off-topic questions: Politely redirect while showing appreciation for their curiosity
        
        **Remember**: You're not just answering questions—you're fostering a love of learning, building confidence, and helping them become independent learners. Make every interaction educational, encouraging, and personally meaningful.
        """
        
        return prompt

    def _structure_response(self, response_text: str, learning_context: Dict, current_module: Optional[str]) -> Dict[str, Any]:
        """Structure plain text response into organized format"""
        
        # Generate contextual suggestions
        suggestions = self._generate_contextual_suggestions(learning_context, current_module)
        
        # Generate learning insights
        insights = self._generate_learning_insights(learning_context)
        
        # Generate recommended actions
        actions = self._generate_recommended_actions(learning_context, current_module)
        
        return {
            "content": response_text,
            "suggestions": suggestions,
            "learning_insights": insights,
            "recommended_actions": actions
        }

    def _generate_contextual_suggestions(self, learning_context: Dict, current_module: Optional[str]) -> List[str]:
        """Generate contextual suggestions based on user's learning state"""
        suggestions = []
        
        total_modules = learning_context.get('total_modules', 0)
        recent_learning = learning_context.get('recent_learning', [])
        learning_level = learning_context.get('learning_level', 'Beginner')
        preferred_subjects = learning_context.get('preferred_subjects', [])
        
        # Current module specific suggestions
        if current_module:
            suggestions.extend([
                f"Can you explain the key concepts in {current_module}?",
                f"What are some practical examples of {current_module}?",
                f"How does {current_module} connect to real-world applications?",
                f"What are common mistakes when learning {current_module}?"
            ])
        
        # Learning level specific suggestions
        if learning_level == "Beginner":
            suggestions.extend([
                "What are the fundamentals I should focus on?",
                "Can you break this concept down into simpler terms?",
                "What prerequisites do I need for advanced topics?"
            ])
        elif learning_level == "Intermediate":
            suggestions.extend([
                "How can I apply this knowledge to a project?",
                "What are advanced techniques I should explore?",
                "Can you suggest challenging practice exercises?"
            ])
        else:  # Advanced
            suggestions.extend([
                "What are the latest developments in this field?",
                "How can I optimize my approach to this problem?",
                "What are alternative methodologies I should consider?"
            ])
        
        # Recent learning connections
        if recent_learning:
            latest_topic = recent_learning[-1]
            suggestions.extend([
                f"How does this relate to what I learned about {latest_topic}?",
                f"Can you help me connect the dots with {latest_topic}?",
                f"Help me review and expand on {latest_topic}"
            ])
        
        # Always include general learning support
        suggestions.extend([
            "What study strategies work best for this topic?",
            "Can you create a quick quiz to test my understanding?",
            "What resources would help me learn this better?",
            "How can I remember this information more effectively?"
        ])
        
        return suggestions[:6]  # Return top 6 most relevant

    def _generate_learning_insights(self, learning_context: Dict) -> List[str]:
        """Generate personalized learning insights based on user's progress and patterns"""
        insights = []
        
        total_modules = learning_context.get('total_modules', 0)
        learning_level = learning_context.get('learning_level', 'Beginner')
        recent_learning = learning_context.get('recent_learning', [])
        preferred_subjects = learning_context.get('preferred_subjects', [])
        learning_streak = learning_context.get('learning_streak', 0)
        
        # Progress-based insights
        if total_modules == 0:
            insights.append("🌱 You're at the exciting beginning of your learning journey - every expert was once a beginner!")
        elif total_modules < 3:
            insights.append("🏗️ You're building a solid foundation - consistency is key to long-term success")
        elif total_modules < 8:
            insights.append("📈 You're developing intermediate skills and showing great learning momentum!")
        elif total_modules < 15:
            insights.append("🎯 You're becoming proficient across multiple areas - consider specializing in your strongest interests")
        else:
            insights.append("🏆 You're an advanced learner with extensive knowledge - time to mentor others!")
        
        # Learning pattern insights
        if len(recent_learning) >= 3:
            # Analyze learning patterns
            if len(set(recent_learning)) == len(recent_learning):
                insights.append("🔄 You're exploring diverse topics - great for building broad knowledge!")
            else:
                insights.append("🎯 You're deepening your knowledge in specific areas - focused learning approach!")
        
        # Subject preference insights
        if preferred_subjects:
            if len(preferred_subjects) == 1:
                insights.append(f"🔬 You show strong focus in {preferred_subjects[0]} - consider exploring related advanced topics")
            elif len(preferred_subjects) >= 3:
                insights.append("🌐 You're a well-rounded learner across multiple disciplines - great for interdisciplinary thinking!")
        
        # Level-specific insights
        if learning_level == "Beginner":
            insights.append("💡 Focus on understanding 'why' concepts work, not just 'how' - this builds deeper comprehension")
        elif learning_level == "Intermediate":
            insights.append("🛠️ Time to apply your knowledge to practical projects - learning by doing accelerates skill development")
        else:  # Advanced
            insights.append("🎓 Consider teaching others or contributing to open-source projects - teaching solidifies expertise")
        
        # Motivational insights based on streak
        if learning_streak >= 10:
            insights.append("🔥 Your consistent learning habit is impressive - you're building skills that compound over time!")
        elif learning_streak >= 5:
            insights.append("⚡ You're developing a strong learning rhythm - keep the momentum going!")
        
        # Learning style insights (inferred from behavior)
        if total_modules >= 5:
            insights.append("📊 Based on your progress, you respond well to structured learning - consider setting specific learning goals")
        
        return insights[:4]  # Return top 4 most relevant insights

    def _generate_recommended_actions(self, learning_context: Dict, current_module: Optional[str]) -> List[str]:
        """Generate recommended learning actions"""
        actions = []
        
        if current_module:
            actions.extend([
                f"Complete the assignments for {current_module}",
                f"Take the quiz to test your understanding",
                f"Watch recommended videos for {current_module}"
            ])
        
        total_modules = learning_context.get('total_modules', 0)
        
        if total_modules == 0:
            actions.append("Start with a beginner-friendly module")
        elif total_modules > 0:
            actions.append("Continue to the next module in your learning path")
        
        actions.extend([
            "Review your notes regularly",
            "Practice with hands-on exercises",
            "Join study groups or discussions"
        ])
        
        return actions[:4]  # Return top 4

    def _assess_learning_level(self, modules_count: int) -> str:
        """Assess user's learning level based on completed modules"""
        if modules_count < 3:
            return "Beginner"
        elif modules_count < 8:
            return "Intermediate"
        else:
            return "Advanced"

    def _extract_subjects(self, module_topics: List[str]) -> List[str]:
        """Extract main subjects from module topics"""
        subjects = set()
        
        for topic in module_topics:
            # Simple keyword extraction
            words = topic.lower().split()
            for word in words:
                if word in ['python', 'javascript', 'react', 'data', 'science', 'machine', 'learning', 'web', 'development']:
                    subjects.add(word.title())
        
        return list(subjects)[:3]  # Return top 3 subjects

    def _update_conversation_history(self, user_id: int, user_message: str, assistant_response: str):
        """Update conversation history for user"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        
        self.user_contexts[user_id].append({
            "user": user_message,
            "assistant": assistant_response
        })
        
        # Keep only last 10 exchanges
        if len(self.user_contexts[user_id]) > 10:
            self.user_contexts[user_id] = self.user_contexts[user_id][-10:]

    def _generate_fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate intelligent fallback response when AI is not available"""
        
        message_lower = message.lower()
        
        # Analyze the message and provide relevant responses
        if any(word in message_lower for word in ['python', 'list', 'array']):
            response = "Python lists are ordered collections that can store multiple items! They're like containers where you can put different values. For example: my_list = [1, 2, 3]. What specific aspect would you like to learn about?"
            suggestions = [
                "How do I create a Python list?",
                "What are list methods?", 
                "Show me list examples",
                "How do I access list items?"
            ]
        elif any(word in message_lower for word in ['javascript', 'react', 'hook']):
            response = "React hooks are functions that let you use state and other React features! They make components more powerful. Would you like to learn about useState, useEffect, or other hooks?"
            suggestions = [
                "Explain useState hook",
                "What is useEffect?",
                "Show me hook examples", 
                "How do hooks work?"
            ]
        elif any(word in message_lower for word in ['function', 'method']):
            response = "Functions are reusable blocks of code that perform specific tasks! They help organize your code and avoid repetition. What would you like to know about functions?"
            suggestions = [
                "How do I create a function?",
                "What are function parameters?",
                "Show function examples",
                "Explain return values"
            ]
        elif any(word in message_lower for word in ['help', 'confused', 'stuck']):
            response = "I'm here to help you understand! Learning programming can be challenging, but breaking it down step by step makes it easier. What specific topic is giving you trouble?"
            suggestions = [
                "Explain this concept simply",
                "Give me an example",
                "What are the basics?",
                "How does this work?"
            ]
        else:
            response = "Great question! I'm here to help you learn programming concepts. Whether it's Python, JavaScript, React, or any other topic, I can provide explanations and examples. What would you like to explore?"
            suggestions = [
                "Explain a programming concept",
                "Show me code examples",
                "Help with current topic",
                "Give study tips"
            ]
        
        return {
            "response": response,
            "suggestions": suggestions,
            "learning_insights": [
                "Practice coding regularly to build muscle memory",
                "Don't hesitate to experiment with code - it's the best way to learn!"
            ],
            "recommended_actions": [
                "Try coding along with examples",
                "Practice the concepts you learn",
                "Ask questions when something isn't clear",
                "Build small projects to apply your knowledge"
            ],
            "context_used": False
        }

    def clear_conversation_history(self, user_id: int):
        """Clear conversation history for a user"""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]

    def get_conversation_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of user's conversation history"""
        history = self.user_contexts.get(user_id, [])
        
        return {
            "total_exchanges": len(history),
            "recent_topics": self._extract_recent_topics(history),
            "conversation_start": len(history) > 0
        }

    def _extract_recent_topics(self, history: List[Dict]) -> List[str]:
        """Extract recent topics from conversation history"""
        topics = []
        for exchange in history[-5:]:  # Last 5 exchanges
            user_message = exchange.get('user', '').lower()
            # Simple topic extraction
            if 'python' in user_message:
                topics.append('Python')
            elif 'javascript' in user_message:
                topics.append('JavaScript')
            elif 'react' in user_message:
                topics.append('React')
            # Add more topic extraction logic as needed
        
        return list(set(topics))  # Remove duplicates
