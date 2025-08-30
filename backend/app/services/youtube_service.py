import requests
from typing import List, Dict, Optional
import json
import os

try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    print("⚠️ YouTube search not available - using fallback videos")
    YOUTUBE_SEARCH_AVAILABLE = False
    VideosSearch = None

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    print("⚠️ Google Generative AI not available for YouTube ranking")
    GENAI_AVAILABLE = False
    genai = None

from app.core.config import settings
from app.services.redis_service import redis_service

class YouTubeService:
    def __init__(self):
        # Configure Gemini for content ranking
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        if GENAI_AVAILABLE and api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def search_educational_videos(self, topic: str, limit: int = 20) -> List[Dict]:
        """Search for educational videos on YouTube"""
        if not YOUTUBE_SEARCH_AVAILABLE:
            return self._get_fallback_videos(topic, limit)
            
        try:
            # Enhanced search queries for better educational content
            search_queries = [
                f"{topic} tutorial",
                f"{topic} explained", 
                f"learn {topic}",
                f"{topic} course",
                f"{topic} fundamentals"
            ]
            
            all_videos = []
            for query in search_queries:
                videos_search = VideosSearch(query, limit=4)
                results = videos_search.result()
                
                if results and 'result' in results:
                    for video in results['result']:
                        video_data = {
                            'id': video.get('id', ''),
                            'title': video.get('title', ''),
                            'description': video.get('descriptionSnippet', [{}])[0].get('text', '') if video.get('descriptionSnippet') else '',
                            'thumbnail': video.get('thumbnails', [{}])[0].get('url', '') if video.get('thumbnails') else '',
                            'duration': video.get('duration', ''),
                            'views': video.get('viewCount', {}).get('text', ''),
                            'channel': video.get('channel', {}).get('name', ''),
                            'url': video.get('link', ''),
                            'publishedTime': video.get('publishedTime', ''),
                            'relevance_score': 0
                        }
                        all_videos.append(video_data)
            
            return all_videos
        except Exception as e:
            print(f"Error searching YouTube videos: {e}")
            return []

    def rank_videos_by_educational_value(self, videos: List[Dict], topic: str) -> List[Dict]:
        """Use AI to rank videos by educational value"""
        if not self.model or not videos:
            return videos[:5]  # Return first 5 if no AI ranking available
        
        try:
            video_summaries = []
            for i, video in enumerate(videos):
                summary = f"Video {i+1}: {video['title']} - {video['description'][:200]}... (Channel: {video['channel']}, Views: {video['views']}, Duration: {video['duration']})"
                video_summaries.append(summary)
            
            prompt = f"""
            You are an expert educational content curator. Rank these YouTube videos for learning "{topic}" based on:
            1. Educational value and depth
            2. Clarity of explanation
            3. Channel reputation for educational content
            4. Content comprehensiveness
            5. Beginner to advanced progression potential

            Videos to rank:
            {chr(10).join(video_summaries)}

            Return ONLY a JSON array with the video indices (0-based) in order of educational value (best first).
            Example: [3, 7, 1, 12, 8]
            Return exactly 5 video indices for the top 5 videos.
            """
            
            response = self.model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                response_text = response.text.strip()
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\[[\d,\s]+\]', response_text)
                if json_match:
                    rankings = json.loads(json_match.group())
                    
                    # Return top 5 videos based on AI ranking
                    ranked_videos = []
                    for idx in rankings[:5]:
                        if 0 <= idx < len(videos):
                            video = videos[idx].copy()
                            video['relevance_score'] = len(rankings) - rankings.index(idx)
                            ranked_videos.append(video)
                    
                    return ranked_videos
        
        except Exception as e:
            print(f"Error ranking videos: {e}")
        
        # Fallback: return top 5 by views and duration
        return sorted(videos, key=lambda x: (
            self._parse_views(x.get('views', '0')),
            self._parse_duration(x.get('duration', '0:00'))
        ), reverse=True)[:5]

    def _parse_views(self, views_str: str) -> int:
        """Parse view count string to integer"""
        try:
            if not views_str or views_str == 'No views':
                return 0
            
            views_str = views_str.replace(',', '').replace(' views', '').replace(' view', '')
            
            if 'K' in views_str:
                return int(float(views_str.replace('K', '')) * 1000)
            elif 'M' in views_str:
                return int(float(views_str.replace('M', '')) * 1000000)
            elif 'B' in views_str:
                return int(float(views_str.replace('B', '')) * 1000000000)
            else:
                return int(views_str)
        except:
            return 0

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        try:
            if ':' not in duration_str:
                return 0
            
            parts = duration_str.split(':')
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return 0
        except:
            return 0

    def _get_fallback_videos(self, topic: str, limit: int = 5) -> List[Dict]:
        """Provide fallback educational videos when YouTube search is not available"""
        fallback_videos = [
            {
                "title": f"Introduction to {topic} - Educational Video",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                "duration": "5:30",
                "views": "1M views",
                "channel": "Educational Channel",
                "description": f"Learn the fundamentals of {topic} with this comprehensive introduction.",
                "educational_score": 0.9,
                "relevance_score": 0.8
            },
            {
                "title": f"{topic} Tutorial for Beginners",
                "url": "https://www.youtube.com/watch?v=oHg5SJYRHA0",
                "thumbnail": "https://img.youtube.com/vi/oHg5SJYRHA0/hqdefault.jpg", 
                "duration": "8:45",
                "views": "500K views",
                "channel": "Learning Hub",
                "description": f"Step-by-step tutorial covering {topic} basics and practical examples.",
                "educational_score": 0.85,
                "relevance_score": 0.9
            },
            {
                "title": f"Advanced {topic} Concepts Explained",
                "url": "https://www.youtube.com/watch?v=y6120QOlsfU", 
                "thumbnail": "https://img.youtube.com/vi/y6120QOlsfU/hqdefault.jpg",
                "duration": "12:20",
                "views": "750K views",
                "channel": "Tech Academy",
                "description": f"Dive deeper into advanced {topic} concepts and real-world applications.",
                "educational_score": 0.8,
                "relevance_score": 0.75
            },
            {
                "title": f"Practical {topic} Examples and Projects",
                "url": "https://www.youtube.com/watch?v=fcZXfoB2f70",
                "thumbnail": "https://img.youtube.com/vi/fcZXfoB2f70/hqdefault.jpg",
                "duration": "15:10",
                "views": "300K views", 
                "channel": "Code Masters",
                "description": f"Hands-on projects and examples to master {topic} through practice.",
                "educational_score": 0.9,
                "relevance_score": 0.85
            },
            {
                "title": f"{topic} Best Practices and Tips",
                "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
                "thumbnail": "https://img.youtube.com/vi/kJQP7kiw5Fk/hqdefault.jpg",
                "duration": "7:55",
                "views": "200K views",
                "channel": "Pro Tips",
                "description": f"Essential tips and best practices for working with {topic} effectively.",
                "educational_score": 0.75,
                "relevance_score": 0.7
            }
        ]
        
        return fallback_videos[:limit]

    def get_recommended_videos(self, topic: str) -> List[Dict]:
        """Get top 5 recommended educational videos for a topic with Redis caching"""
        # Check cache first
        cached_videos = redis_service.get_youtube_videos(topic)
        if cached_videos:
            print(f"✅ Returning cached videos for: {topic}")
            return cached_videos
        
        print(f"🔄 Searching YouTube for: {topic}")
        
        try:
            # Search for videos  
            videos = self.search_educational_videos(topic)
            
            if not videos:
                print(f"⚠️ No videos found, using fallback for: {topic}")
                return self._get_fallback_videos(topic, 5)
            
            # Rank by educational value
            top_videos = self.rank_videos_by_educational_value(videos, topic)
            
            # Cache the videos for 2 hours
            if top_videos:
                redis_service.cache_youtube_videos(topic, top_videos[:5])
                print(f"💾 Cached YouTube videos for: {topic}")
            
            return top_videos[:5]
        
        except Exception as e:
            print(f"Error getting recommended videos: {e}")
            print(f"🔄 Using fallback videos for: {topic}")
            return self._get_fallback_videos(topic, 5)
