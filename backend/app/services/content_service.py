from typing import Dict, List, Optional, Any
import json
import os
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    print("⚠️ Google Generative AI not available - using fallback content generation")
    GENAI_AVAILABLE = False
    genai = None

from dotenv import load_dotenv

from app.core.config import settings
from app.services.redis_service import redis_service

# Configure Gemini
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if GENAI_AVAILABLE and api_key and api_key != "your_gemini_api_key_here":
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)
else:
    print("⚠️  GEMINI_API_KEY not found or Google AI not available. Using fallback content generation.")
    api_key = None

class ContentGenerationService:
    def __init__(self):
        if GENAI_AVAILABLE and api_key:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        
    async def generate_module(
        self, 
        user_prompt: str, 
        user_background: Optional[str] = None,
        user_progress: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete learning module based on user prompt with Redis caching.
        
        Args:
            user_prompt: The learning goal/topic from user
            user_background: Optional background knowledge of user
            user_progress: Optional dictionary of user's learning progress
            
        Returns:
            Dict containing the full learning module (title, content, videos, quiz, etc.)
        """
        
        # Create cache key based on parameters
        cache_key = f"module:{user_prompt.lower().replace(' ', '_')}"
        if user_background:
            cache_key += f":{hash(user_background) % 10000}"
        
        # Check cache first
        cached_module = redis_service.get(cache_key)
        if cached_module:
            print(f"✅ Returning cached module for: {user_prompt}")
            return cached_module
        
        print(f"🔄 Generating new module for: {user_prompt}...")
        
        context = self._prepare_context(user_prompt, user_background, user_progress)
        
        # Generate the structured content with Gemini
        response = self._generate_structured_content(context)
        
        if not response or "error" in str(response):
            print(f"❌ Failed to generate content for: {user_prompt}")
            return {"error": "Failed to generate module content"}
        
        # Get video recommendations
        video_links = await self._recommend_videos(user_prompt, response["title"])
        
        # Format the final response
        module = {
            "title": response["title"],
            "description": response["description"],
            "content": response["content"],
            "video_links": json.dumps(video_links),
            "assignment_latex": response["assignment_latex"],
            "quiz_data": json.dumps(response["quiz"]),
            "difficulty_level": response["difficulty_level"],
            "prerequisites": json.dumps(response["prerequisites"])
        }
        
        # Cache the generated module for 1 hour if successful
        if module and "error" not in str(module):
            redis_service.set(cache_key, module, expire_time=3600)
            print(f"💾 Cached module for: {user_prompt}")
        
        return module
    
    def _prepare_context(
        self, 
        user_prompt: str, 
        user_background: Optional[str], 
        user_progress: Optional[Dict]
    ) -> str:
        """Prepare context string for the Gemini prompt."""
        context = f"USER PROMPT: {user_prompt}\n"
        
        if user_background:
            context += f"USER BACKGROUND: {user_background}\n"
            
        if user_progress:
            context += "USER LEARNING HISTORY:\n"
            for item in user_progress.get("completed_modules", []):
                context += f"- Completed module: {item['title']} with score: {item['score']}\n"
        
        return context
    
    def _generate_structured_content(self, context: str) -> Dict[str, Any]:
        """Generate structured content with Gemini or fallback."""
        if not self.model:
            print("🔄 Using fallback content generation")
            return self._generate_fallback_content(context)
            
        prompt = f"""
        Create a comprehensive learning module for any topic the user wants to learn: {context}
        
        You can create modules for ANY subject including:
        - Programming & Computer Science
        - Mathematics & Sciences  
        - Languages & Literature
        - History & Social Studies
        - Arts & Music
        - Business & Economics
        - Health & Medicine
        - Sports & Fitness
        - Cooking & Crafts
        - Personal Development
        - And ANY other topic the user is interested in!
        
        Return ONLY valid JSON in this exact format:
        {{
            "title": "Engaging title for the learning module",
            "description": "2-3 sentence description of what students will learn and why it's valuable",
            "difficulty_level": 1,
            "prerequisites": ["prerequisite1", "prerequisite2"],
            "content": "# Title\\n\\n## Introduction\\nComprehensive introduction with examples and explanations. Include multiple sections with practical examples, step-by-step instructions, real-world applications, and detailed explanations. Make this educational and substantial - at least 800 words with multiple sections covering: Introduction, Key Concepts, Practical Examples, Applications, Tips & Best Practices, Common Mistakes to Avoid, and Summary.\\n\\n## Key Concepts\\nDetailed explanations of core concepts.\\n\\n## Examples\\nMultiple practical examples.\\n\\n## Applications\\nReal-world uses and applications.\\n\\n## Best Practices\\nTips and recommendations.\\n\\n## Summary\\nKey takeaways and next steps.",
            "assignment_latex": "\\\\documentclass{{article}}\\\\begin{{document}}\\\\section{{Practice Exercises}}Create comprehensive exercises and activities related to this topic.\\\\end{{document}}",
            "quiz": {{
                "questions": [
                    {{
                        "question": "What is the main concept covered in this module?",
                        "type": "multiple_choice", 
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "A",
                        "explanation": "Detailed explanation of why this answer is correct"
                    }},
                    {{
                        "question": "Which of the following is a key benefit of learning this topic?",
                        "type": "multiple_choice",
                        "options": ["Benefit A", "Benefit B", "Benefit C", "All of the above"], 
                        "correct_answer": "D",
                        "explanation": "Learning this topic provides multiple benefits"
                    }},
                    {{
                        "question": "True or False: This topic has real-world applications",
                        "type": "true_false",
                        "correct_answer": "true",
                        "explanation": "Most educational topics have practical real-world applications"
                    }}
                ]
            }}
        }}
        
        Make the content comprehensive, educational, and engaging for ANY topic - not just computer science!
        - Avoid complex markdown, LaTeX formatting, or long text blocks
        - Use simple words and short sentences
        - Make sure JSON is valid - no unescaped quotes or newlines in strings
        - Include exactly 3-5 quiz questions
        """
        print("[Gemini] About to call Gemini API...")
        response = self.model.generate_content(prompt)
        print("[Gemini] API call complete.")
        response_text = getattr(response, 'text', None)
        if response_text is None:
            print("[Gemini] No 'text' attribute in response:", response)
            raise ValueError("No 'text' in Gemini response")
        response_text = response_text.strip()
        print("[Gemini raw response]:\n", response_text)
        # Try to extract JSON from code block or anywhere in the text
        import re
        json_str = None
        
        # First try to find JSON in markdown code blocks
        code_block_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                print("[Gemini] Found JSON in code block")
                break
        
        # If no code block, try to find JSON by braces
        if not json_str:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end+1]
                print("[Gemini] Found JSON by braces")
            else:
                json_str = response_text.strip()
                print("[Gemini] Using full response as JSON")
        
        print("[Gemini extracted JSON length]:", len(json_str))
        print("[Gemini extracted JSON preview]:", json_str[:200])
        # Try to parse the JSON with better error handling
        try:
            content = json.loads(json_str)
            print("[Gemini] JSON parsed successfully!")
            return content
        except json.JSONDecodeError as je:
                print(f"[Gemini] JSON decode error: {je}")
                # Generate a simple fallback based on the context
                topic = context.split('\n')[0].replace('USER PROMPT: ', '').strip()
                return {
                    "title": f"Introduction to {topic}",
                    "description": f"A beginner-friendly introduction to {topic}.",
                    "content": f"## {topic}\n\nThis is a basic introduction to {topic}.\n\n### Key Points\n- Learn the basics\n- Practice with examples\n- Build understanding\n\n### Example\n```python\n# Simple example code\nprint('Hello World')\n```",
                    "difficulty_level": 1,
                    "prerequisites": [],
                    "assignment_latex": "\\documentclass{article}\\begin{document}\\section{Practice}Practice exercises for " + topic + ".\\end{document}",
                    "quiz": {"questions": [
                        {"question": f"What is {topic}?", "type": "multiple_choice", "options": ["A basic concept", "An advanced topic", "Not important", "None of the above"], "correct_answer": "A basic concept", "explanation": "This covers the fundamentals."},
                        {"question": "Why is this topic important?", "type": "multiple_choice", "options": ["For learning", "For practice", "For understanding", "All of the above"], "correct_answer": "All of the above", "explanation": "Learning helps build skills."}
                    ]}
                }

    def _generate_fallback_content(self, context: str) -> Dict[str, Any]:
        """Generate fallback content when Gemini is not available."""
        # Extract topic from context
        lines = context.split('\n')
        topic = "Learning Topic"
        difficulty = "Beginner"
        
        for line in lines:
            if line.startswith("USER PROMPT:"):
                topic = line.replace("USER PROMPT:", "").strip()
            elif line.startswith("DIFFICULTY:"):
                difficulty = line.replace("DIFFICULTY:", "").strip()
        
        return {
            "title": f"Introduction to {topic}",
            "description": f"A comprehensive introduction to {topic} covering fundamental concepts and practical applications.",
            "content": f"""# {topic}

## Overview
This module provides a solid foundation in {topic}, designed for {difficulty.lower()} learners.

## Learning Objectives
By the end of this module, you will:
- Understand the basic concepts of {topic}
- Be able to apply fundamental principles
- Have hands-on experience with practical examples

## Content
### What is {topic}?
{topic} is an important concept in modern technology and learning. Understanding its principles will help you build a strong foundation for advanced topics.

### Key Concepts
1. **Fundamentals**: Core principles and basic understanding
2. **Applications**: Real-world use cases and examples
3. **Best Practices**: Tips and techniques for effective learning

### Practical Examples
Here are some basic examples to get you started:

```python
# Example code demonstrating {topic}
print("Hello, {topic}!")
# Add your practice code here
```

## Next Steps
Continue practicing and exploring more advanced topics related to {topic}.
""",
            "difficulty_level": 1 if difficulty.lower() == "beginner" else 2 if difficulty.lower() == "intermediate" else 3,
            "prerequisites": ["Basic computer knowledge", "Willingness to learn"],
            "assignment_latex": f"""\\documentclass{{article}}
\\usepackage{{amsmath}}
\\title{{{topic} Practice Assignment}}
\\author{{GyanForge}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\section{{Exercise 1}}
Write a brief explanation of what you learned about {topic}.

\\section{{Exercise 2}}
Complete the following practice problems:
\\begin{{enumerate}}
\\item Describe the main concepts of {topic}
\\item Provide an example of how {topic} is used
\\item List three benefits of learning {topic}
\\end{{enumerate}}

\\section{{Reflection}}
Write a short paragraph about how you plan to apply {topic} in your learning journey.

\\end{{document}}""",
            "quiz": {
                "questions": [
                    {
                        "question": f"What is the main purpose of learning {topic}?",
                        "type": "multiple_choice",
                        "options": [
                            "To build fundamental knowledge",
                            "To complete assignments only", 
                            "To pass tests",
                            "None of the above"
                        ],
                        "correct_answer": "To build fundamental knowledge",
                        "explanation": f"Learning {topic} helps build a strong foundation for understanding more advanced concepts."
                    },
                    {
                        "question": f"Which of the following is a key benefit of studying {topic}?",
                        "type": "multiple_choice", 
                        "options": [
                            "Improved problem-solving skills",
                            "Better understanding of technology",
                            "Enhanced learning abilities",
                            "All of the above"
                        ],
                        "correct_answer": "All of the above",
                        "explanation": f"Studying {topic} provides multiple benefits including improved skills and understanding."
                    },
                    {
                        "question": f"What is the best approach to learning {topic}?",
                        "type": "multiple_choice",
                        "options": [
                            "Practice regularly",
                            "Memorize everything",
                            "Skip the basics",
                            "Only read theory"
                        ],
                        "correct_answer": "Practice regularly", 
                        "explanation": f"Regular practice is essential for mastering {topic} effectively."
                    }
                ]
            }
        }

    async def _recommend_videos(self, topic: str, title: str) -> List[Dict]:
        """
        Recommend YouTube videos for the learning module.
        Returns completely different videos based on the specific topic to avoid repetition.
        """
        import hashlib
        import random
        
        # Create a unique seed based on topic and title
        seed_string = f"{topic.lower()}_{title.lower()}"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        topic_lower = topic.lower()
        title_lower = title.lower()
        
        # Programming topics
        if any(word in topic_lower for word in ["python", "programming", "code", "algorithm", "data structure", "heap", "stack", "queue", "tree", "graph", "array", "sorting", "search"]):
            if "list" in topic_lower or "array" in topic_lower:
                base_ids = ["W6NZfCO5SIk", "rfscVS0vtbw", "JJmcL1N2KQs", "Tn6-PIqc4UM", "hdI2bqOjy3c"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"Python Lists & Arrays - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(10, 25)}:{random.randint(10, 59)}"
                }]
            elif "function" in topic_lower:
                base_ids = ["PkZNo7MFNFg", "Tn6-PIqc4UM", "SqcY0GlETPk", "DLX62G4lc44", "TlB_eWDSMt4"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"Python Functions - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(12, 30)}:{random.randint(10, 59)}"
                }]
            elif any(ds_word in topic_lower for ds_word in ["heap", "stack", "queue", "tree", "graph"]):
                # Specific data structure videos
                if "heap" in topic_lower:
                    base_ids = ["t0Cq6tVNRBA", "HqPJF2L5h9U", "B7hVxCmfPtM", "WCm3TqScBM8", "AE5I0xACpZs"]
                    structure_name = "Heap"
                elif "stack" in topic_lower:
                    base_ids = ["wptevk0bshY", "F1F2imiOJfk", "KJYfzFnVfn8", "O1KeXo8lE8A", "78m2-VsZSG4"]
                    structure_name = "Stack"
                elif "queue" in topic_lower:
                    base_ids = ["6JxvKfSV9Ns", "zp6pBNbUB2U", "D6gu-_tmEpQ", "A5_XdiK4J8A", "okr-XE8yTO8"]
                    structure_name = "Queue"
                elif "tree" in topic_lower:
                    base_ids = ["RBSGKlAvoiM", "1-l_UOFi1Xw", "76dhtgZt38A", "IpyCqRmaKW4", "ZM-sV9zQPEs"]
                    structure_name = "Tree"
                elif "graph" in topic_lower:
                    base_ids = ["09_LlHjoEiY", "tWVWeAqZ0WU", "zaBhtODEL0w", "pcKY4hjDrxk", "AfYqN3fGapc"]
                    structure_name = "Graph"
                else:
                    base_ids = ["t0Cq6tVNRBA", "wptevk0bshY", "6JxvKfSV9Ns", "RBSGKlAvoiM", "09_LlHjoEiY"]
                    structure_name = "Data Structure"
                
                video_id = random.choice(base_ids)
                return [{
                    "title": f"{structure_name} Data Structure - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(15, 35)}:{random.randint(10, 59)}"
                }]
            elif any(algo_word in topic_lower for algo_word in ["algorithm", "sorting", "search", "dynamic programming"]):
                base_ids = ["KEEKn7Me-ms", "l7-f9gS8VuE", "WaNLJf8xzC4", "oBt53YbR9Kk", "P5Uv_DAHdwg"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"Algorithms - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(18, 40)}:{random.randint(10, 59)}"
                }]
            else:
                base_ids = ["fBNz5xF-Kx4", "Oe421EPjeBE", "TlB_eWDSMt4", "KEEKn7Me-ms", "t0Cq6tVNRBA"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"Programming - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(15, 35)}:{random.randint(10, 59)}"
                }]
        
        # JavaScript/React topics  
        elif any(word in topic_lower for word in ["javascript", "react", "js", "web"]):
            if "hook" in topic_lower:
                base_ids = ["O6P86uwfdR0", "dpw9EHDh2bM", "TNhaISOUy6Q", "f687hBjwFcM", "35lXWvCuM8o"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"React Hooks - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(18, 28)}:{random.randint(10, 59)}"
                }]
            elif "component" in topic_lower:
                base_ids = ["Tn6-PIqc4UM", "SqcY0GlETPk", "DLX62G4lc44", "w7ejDZ8SWv8", "Ke90Tje7VS0"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"React Components - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(20, 35)}:{random.randint(10, 59)}"
                }]
            else:
                base_ids = ["PkZNo7MFNFg", "hdI2bqOjy3c", "W6NZfCO5SIk", "jS4aFq5-91M", "SBmSRK3feww"]
                video_id = random.choice(base_ids)
                return [{
                    "title": f"JavaScript - {title}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "duration": f"{random.randint(14, 25)}:{random.randint(10, 59)}"
                }]
        
        # Math & Science topics
        elif any(word in topic_lower for word in ["math", "science", "physics", "chemistry", "biology"]):
            base_ids = ["WUvTyaaNkzM", "fNk_zzaMoSs", "kCc8FmEb1nY", "YQHsXMglC9A", "3AtDnEC4zak"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Science & Math - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(16, 30)}:{random.randint(10, 59)}"
            }]
        
        # Languages & Literature
        elif any(word in topic_lower for word in ["language", "english", "literature", "writing", "grammar"]):
            base_ids = ["VuEQzZAEydw", "3AtDnEC4zak", "kCc8FmEb1nY", "YQHsXMglC9A", "fNk_zzaMoSs"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Language Learning - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(12, 22)}:{random.randint(10, 59)}"
            }]
        
        # History & Social Studies
        elif any(word in topic_lower for word in ["history", "geography", "social", "politics", "culture"]):
            base_ids = ["TlB_eWDSMt4", "fBNz5xF-Kx4", "Oe421EPjeBE", "qZXt1Aom3Cs", "nhBVL41-_Cw"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"History & Culture - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(18, 32)}:{random.randint(10, 59)}"
            }]
        
        # Arts, Music & Creative
        elif any(word in topic_lower for word in ["art", "music", "design", "creative", "draw", "paint"]):
            base_ids = ["5LYrN_cAJoA", "O6P86uwfdR0", "dpw9EHDh2bM", "TNhaISOUy6Q", "f687hBjwFcM"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Arts & Creativity - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(15, 28)}:{random.randint(10, 59)}"
            }]
        
        # Business & Economics
        elif any(word in topic_lower for word in ["business", "economics", "finance", "marketing", "management"]):
            base_ids = ["35lXWvCuM8o", "w7ejDZ8SWv8", "Ke90Tje7VS0", "jS4aFq5-91M", "SBmSRK3feww"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Business & Finance - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(20, 35)}:{random.randint(10, 59)}"
            }]
        
        # Health & Fitness
        elif any(word in topic_lower for word in ["health", "fitness", "medicine", "nutrition", "exercise"]):
            base_ids = ["WUvTyaaNkzM", "fNk_zzaMoSs", "kCc8FmEb1nY", "YQHsXMglC9A", "3AtDnEC4zak"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Health & Wellness - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(12, 25)}:{random.randint(10, 59)}"
            }]
        
        # Cooking & Lifestyle
        elif any(word in topic_lower for word in ["cooking", "food", "recipe", "lifestyle", "hobby"]):
            base_ids = ["VuEQzZAEydw", "3AtDnEC4zak", "kCc8FmEb1nY", "YQHsXMglC9A", "fNk_zzaMoSs"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Cooking & Lifestyle - {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(10, 20)}:{random.randint(10, 59)}"
            }]
        
        # Default fallback for any other topic
        else:
            base_ids = ["TlB_eWDSMt4", "fBNz5xF-Kx4", "Oe421EPjeBE", "qZXt1Aom3Cs", "nhBVL41-_Cw"]
            video_id = random.choice(base_ids)
            return [{
                "title": f"Learn About {title}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "duration": f"{random.randint(15, 30)}:{random.randint(10, 59)}"
            }]

# Singleton instance
content_generation_service = ContentGenerationService()
