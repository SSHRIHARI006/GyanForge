import json
import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from .youtube_service import YouTubeService

class ContentService:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyB-Isr6koIa-y7v_X9dsnxLECx_jwB-1ZM')
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("[Gemini] Model initialized successfully")
        else:
            self.model = None
            print("[Gemini] No valid API key found")
        
        # Initialize YouTube service
        self.youtube_service = YouTubeService()

    def generate_comprehensive_module(self, topic: str, difficulty: str = "Beginner") -> Dict[str, Any]:
        """Generate a comprehensive learning module with videos, notes, and assignments"""
        try:
            print(f"[ContentService] Generating comprehensive module for: {topic} ({difficulty})")
            
            # Generate the main educational content
            educational_content = self._generate_educational_content(topic, difficulty)
            
            # Get recommended YouTube videos
            recommended_videos = self.youtube_service.get_recommended_videos(topic)
            
            # Generate notes and assignments
            notes = self._generate_notes(topic, difficulty)
            assignments = self._generate_assignments(topic, difficulty)
            
            # Create comprehensive module
            module = {
                "topic": topic,
                "difficulty": difficulty,
                "content": educational_content,
                "recommended_videos": recommended_videos,
                "notes": notes,
                "assignments": assignments,
                "estimated_duration": self._estimate_learning_duration(educational_content),
                "learning_objectives": self._extract_learning_objectives(educational_content),
                "prerequisites": self._generate_prerequisites(topic, difficulty)
            }
            
            print(f"[ContentService] Successfully generated comprehensive module")
            return module
            
        except Exception as e:
            print(f"[ContentService] Error generating comprehensive module: {e}")
            return self._generate_fallback_module(topic, difficulty)

    def _generate_educational_content(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate detailed educational content"""
        if not self.model:
            return self._generate_fallback_content(topic, difficulty)
        
        prompt = f"""
        Create comprehensive educational content for "{topic}" at {difficulty} level.
        
        Structure your response as a JSON object with:
        {{
            "introduction": "Brief engaging introduction to the topic",
            "key_concepts": ["concept1", "concept2", "concept3"],
            "detailed_explanation": "Comprehensive explanation with examples",
            "practical_examples": [
                {{"title": "Example 1", "description": "...", "code_snippet": "..."}},
                {{"title": "Example 2", "description": "...", "code_snippet": "..."}}
            ],
            "best_practices": ["practice1", "practice2", "practice3"],
            "common_mistakes": ["mistake1", "mistake2"],
            "summary": "Key takeaways and next steps"
        }}
        
        Make it educational, practical, and engaging for {difficulty} learners.
        """
        
        return self._generate_structured_content(prompt, topic, "educational content")

    def _generate_notes(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate structured notes for the topic"""
        if not self.model:
            return self._generate_fallback_notes(topic, difficulty)
        
        prompt = f"""
        Create comprehensive study notes for "{topic}" at {difficulty} level.
        
        Structure as JSON:
        {{
            "title": "Notes: {topic}",
            "sections": [
                {{
                    "heading": "Section heading",
                    "content": "Detailed bullet points and explanations",
                    "key_points": ["point1", "point2", "point3"]
                }}
            ],
            "quick_reference": {{
                "definitions": {{"term1": "definition1", "term2": "definition2"}},
                "formulas": ["formula1", "formula2"],
                "commands": ["command1", "command2"]
            }},
            "study_tips": ["tip1", "tip2", "tip3"]
        }}
        
        Make notes clear, organized, and perfect for review and downloading.
        """
        
        return self._generate_structured_content(prompt, topic, "notes")

    def _generate_assignments(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate practical assignments"""
        if not self.model:
            return self._generate_fallback_assignments(topic, difficulty)
        
        prompt = f"""
        Create 3 practical assignments for "{topic}" at {difficulty} level.
        
        Structure as JSON array:
        [
            {{
                "title": "Assignment 1 Title",
                "description": "What the student needs to do",
                "objectives": ["objective1", "objective2"],
                "instructions": ["step1", "step2", "step3"],
                "expected_outcome": "What they should achieve",
                "difficulty": "{difficulty}",
                "estimated_time": "30 minutes",
                "hints": ["hint1", "hint2"]
            }}
        ]
        
        Make assignments practical, engaging, and appropriate for {difficulty} level.
        """
        
        result = self._generate_structured_content(prompt, topic, "assignments")
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'assignments' in result:
            return result['assignments']
        else:
            return [result] if result else []

    def _generate_structured_content(self, prompt: str, topic: str, content_type: str) -> Dict[str, Any]:
        """Generate structured content using Gemini with robust JSON parsing"""
        try:
            # Check if model is available
            if not self.model:
                print("[Gemini] No model available - using fallback")
                raise Exception("Gemini model not configured")
                
            print("[Gemini] About to call Gemini API...")
            response = self.model.generate_content(prompt)
            print("[Gemini] API call complete.")
            
            response_text = getattr(response, 'text', None)
            if response_text is None:
                print("[Gemini] No 'text' attribute in response:", response)
                raise ValueError("No 'text' in Gemini response")
                
            response_text = response_text.strip()
            print(f"[Gemini raw response length]: {len(response_text)} characters")
            print(f"[Gemini raw response preview]: {response_text[:200]}...")
            
            # Try to extract JSON from code block or anywhere in the text
            import re
            json_pattern = r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object/array in the text
                brace_pattern = r'(\{.*\}|\[.*\])'
                brace_match = re.search(brace_pattern, response_text, re.DOTALL)
                if brace_match:
                    json_str = brace_match.group(1)
                else:
                    json_str = response_text
            
            print(f"[Gemini] Attempting to parse JSON: {json_str[:100]}...")
            
            try:
                result = json.loads(json_str)
                print(f"[Gemini] Successfully parsed JSON for {content_type}")
                return result
            except json.JSONDecodeError as je:
                print(f"[Gemini] JSON decode error: {je}")
                # Try to clean and parse again
                cleaned = self._clean_json_string(json_str)
                try:
                    result = json.loads(cleaned)
                    print(f"[Gemini] Successfully parsed cleaned JSON for {content_type}")
                    return result
                except:
                    print(f"[Gemini] Failed to parse cleaned JSON, using fallback")
                    raise je
                    
        except Exception as e:
            print(f"[Gemini] Error in _generate_structured_content: {e}")
            if content_type == "educational content":
                return self._generate_fallback_content(topic, "Beginner")
            elif content_type == "notes":
                return self._generate_fallback_notes(topic, "Beginner")
            elif content_type == "assignments":
                return self._generate_fallback_assignments(topic, "Beginner")
            else:
                return {"error": f"Failed to generate {content_type}", "topic": topic}

    def _clean_json_string(self, json_str: str) -> str:
        """Clean JSON string for better parsing"""
        # Remove any leading/trailing whitespace
        json_str = json_str.strip()
        
        # Remove any markdown formatting
        json_str = json_str.replace('```json', '').replace('```', '')
        
        # Fix common JSON issues
        json_str = json_str.replace("'", '"')  # Replace single quotes
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
        
        return json_str

    def _estimate_learning_duration(self, content: Dict) -> str:
        """Estimate learning duration based on content"""
        try:
            if isinstance(content, dict) and 'detailed_explanation' in content:
                word_count = len(content['detailed_explanation'].split())
                if word_count > 500:
                    return "2-3 hours"
                elif word_count > 200:
                    return "1-2 hours"
                else:
                    return "30-60 minutes"
        except:
            pass
        return "1-2 hours"

    def _extract_learning_objectives(self, content: Dict) -> List[str]:
        """Extract learning objectives from content"""
        try:
            if isinstance(content, dict):
                if 'key_concepts' in content:
                    return [f"Understand {concept}" for concept in content['key_concepts'][:3]]
                elif 'summary' in content:
                    return ["Master the fundamentals", "Apply practical knowledge", "Build confidence"]
        except:
            pass
        return ["Learn core concepts", "Practice with examples", "Build practical skills"]

    def _generate_prerequisites(self, topic: str, difficulty: str) -> List[str]:
        """Generate prerequisites based on topic and difficulty"""
        if difficulty.lower() == "beginner":
            return ["Basic computer literacy", "Willingness to learn"]
        elif difficulty.lower() == "intermediate":
            return [f"Basic understanding of {topic.split()[0]}", "Some programming experience"]
        else:
            return [f"Strong foundation in {topic.split()[0]}", "Advanced problem-solving skills"]

    # Fallback methods for when AI generation fails
    def _generate_fallback_module(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate fallback module when main generation fails"""
        return {
            "topic": topic,
            "difficulty": difficulty,
            "content": self._generate_fallback_content(topic, difficulty),
            "recommended_videos": [],
            "notes": self._generate_fallback_notes(topic, difficulty),
            "assignments": self._generate_fallback_assignments(topic, difficulty),
            "estimated_duration": "1-2 hours",
            "learning_objectives": ["Learn core concepts", "Practice with examples"],
            "prerequisites": ["Basic knowledge"]
        }

    def _generate_fallback_content(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate fallback content when AI generation fails"""
        return {
            "introduction": f"Welcome to learning about {topic}! This {difficulty.lower()}-level content will help you understand the fundamentals.",
            "key_concepts": [f"{topic} basics", f"{topic} applications", f"{topic} best practices"],
            "detailed_explanation": f"This is an introduction to {topic}. We'll cover the essential concepts step by step, making it accessible for {difficulty.lower()} learners.",
            "practical_examples": [
                {"title": "Basic Example", "description": f"Simple {topic} example", "code_snippet": "// Example code here"},
                {"title": "Advanced Example", "description": f"More complex {topic} usage", "code_snippet": "// Advanced code here"}
            ],
            "best_practices": [f"Follow {topic} conventions", "Write clean code", "Test your understanding"],
            "common_mistakes": ["Rushing through concepts", "Skipping practice"],
            "summary": f"You've learned the basics of {topic}. Continue practicing to master these concepts!"
        }

    def _generate_fallback_notes(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate fallback notes when AI generation fails"""
        return {
            "title": f"Notes: {topic}",
            "sections": [
                {
                    "heading": "Introduction",
                    "content": f"Key points about {topic}",
                    "key_points": [f"{topic} definition", f"{topic} importance", f"{topic} uses"]
                },
                {
                    "heading": "Main Concepts",
                    "content": f"Core concepts of {topic}",
                    "key_points": ["Concept 1", "Concept 2", "Concept 3"]
                }
            ],
            "quick_reference": {
                "definitions": {topic: f"Definition of {topic}"},
                "formulas": [],
                "commands": []
            },
            "study_tips": ["Review regularly", "Practice with examples", "Ask questions"]
        }

    def _generate_fallback_assignments(self, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate fallback assignments when AI generation fails"""
        return [
            {
                "title": f"Introduction to {topic}",
                "description": f"Complete basic exercises related to {topic}",
                "objectives": [f"Understand {topic} basics", "Apply concepts"],
                "instructions": ["Read the material", "Complete exercises", "Submit your work"],
                "expected_outcome": f"Basic understanding of {topic}",
                "difficulty": difficulty,
                "estimated_time": "30 minutes",
                "hints": ["Take your time", "Review examples"]
            },
            {
                "title": f"Practical {topic} Application",
                "description": f"Build a simple project using {topic}",
                "objectives": ["Apply knowledge practically", "Build confidence"],
                "instructions": ["Plan your approach", "Implement solution", "Test your work"],
                "expected_outcome": f"Working {topic} application",
                "difficulty": difficulty,
                "estimated_time": "1 hour",
                "hints": ["Start simple", "Build incrementally"]
            }
        ]

# Legacy support
class ContentGenerationService(ContentService):
    """Legacy class name support"""
    pass
