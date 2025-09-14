"""
AI Recommendation Engine using Google Gemini for Personalized Trip Planning

This service uses Google's Gemini AI to provide intelligent travel recommendations
based on user preferences, swipe patterns, and contextual factors.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class TravelMode(Enum):
    PLEASURE = "pleasure"
    BUSINESS = "business"
    FAMILY = "family"


class TravelScope(Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class SwipeAction(Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class ContentType(Enum):
    DESTINATION = "destination"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    TRANSPORTATION = "transportation"


@dataclass
class UserProfile:
    """User profile with travel preferences"""
    user_id: str
    budget_min: float
    budget_max: float
    group_size: int
    duration_days: int
    travel_mode: TravelMode
    travel_scope: TravelScope
    dietary_preferences: List[str] = None
    transport_preferences: List[str] = None


@dataclass
class TravelContent:
    """Travel content item (destination, hotel, activity, etc.)"""
    content_id: str
    content_type: ContentType
    title: str
    description: str
    image_url: str
    price_min: float
    price_max: float
    location: str
    tags: List[str]
    rating: float
    popularity_score: float


@dataclass
class SwipeInteraction:
    """User swipe interaction record"""
    user_id: str
    content_id: str
    content_type: ContentType
    action: SwipeAction
    timestamp: float
    session_id: str


@dataclass
class RecommendationRequest:
    """Request for AI recommendations"""
    user_profile: UserProfile
    previous_swipes: List[SwipeInteraction]
    content_type: ContentType
    batch_size: int = 20
    exclude_content_ids: List[str] = None


class GeminiRecommendationEngine:
    """AI recommendation engine using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.model = None
        self.model_name = "gemini-1.5-flash"  # Fast and efficient model
        
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini AI engine initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None
        else:
            logger.warning("Gemini API key not found or package not available")
    
    async def _call_ai_model(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Call Gemini AI model with prompt
        
        Args:
            prompt: The prompt to send to Gemini
            temperature: Generation temperature (0.0 to 1.0)
            
        Returns:
            AI response content
        """
        if not self.model:
            raise RuntimeError("Gemini AI client not available")
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2000,
                top_p=0.8,
                top_k=40
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini AI model call failed: {e}")
            raise
    
    async def analyze_user_preferences(self, swipe_history: List[SwipeInteraction]) -> Dict[str, Any]:
        """
        Analyze user's swipe patterns to extract preferences using Gemini
        
        Args:
            swipe_history: List of user's swipe interactions
            
        Returns:
            Dict containing extracted preferences and patterns
        """
        if not swipe_history:
            return {"preferences": {}, "patterns": {}, "confidence": 0.0}
        
        if not self.model:
            return {"preferences": {}, "patterns": {}, "confidence": 0.0, "error": "Gemini AI client not available"}
        
        # Aggregate swipe data
        likes = [s for s in swipe_history if s.action == SwipeAction.LIKE]
        dislikes = [s for s in swipe_history if s.action == SwipeAction.DISLIKE]
        
        # Create analysis prompt
        prompt = f"""You are an expert travel preference analyst. Analyze user swipe patterns to extract travel preferences.

LIKED CONTENT ({len(likes)} items):
{json.dumps([asdict(like) for like in likes[:10]], indent=2)}

DISLIKED CONTENT ({len(dislikes)} items):
{json.dumps([asdict(dislike) for dislike in dislikes[:10]], indent=2)}

Based on this data, extract the user's travel preferences as a JSON object with the following structure:
{{
    "preferences": {{
        "preferred_content_types": ["accommodation", "activity"],
        "price_range_preference": "budget|mid-range|luxury",
        "location_preferences": ["beach", "mountains", "cities"],
        "feature_preferences": ["wifi", "spa", "pool"]
    }},
    "patterns": {{
        "swipe_frequency": "high|medium|low",
        "decision_speed": "fast|moderate|slow"
    }},
    "confidence": 0.85
}}

Focus on identifying patterns in content types, price ranges, locations, and features they prefer.
Return only valid JSON, no additional text."""
        
        try:
            response_content = await self._call_ai_model(prompt, temperature=0.2)
            
            # Clean and parse JSON response
            clean_response = response_content.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:-3]
            elif clean_response.startswith('```'):
                clean_response = clean_response[3:-3]
            
            analysis = json.loads(clean_response)
            logger.info(f"Analyzed preferences for {len(swipe_history)} swipes")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing preferences with Gemini: {e}")
            return {"preferences": {}, "patterns": {}, "confidence": 0.0}
    
    async def generate_recommendations(self, 
                               request: RecommendationRequest,
                               available_content: List[TravelContent]) -> List[Tuple[TravelContent, float]]:
        """
        Generate personalized recommendations using Gemini AI
        
        Args:
            request: Recommendation request with user profile and preferences
            available_content: Pool of available travel content
            
        Returns:
            List of (content, relevance_score) tuples sorted by relevance
        """
        if not available_content:
            return []
        
        if not self.model:
            return self._fallback_recommendations(request, available_content)
        
        # Analyze user preferences from swipe history
        user_preferences = await self.analyze_user_preferences(request.previous_swipes)
        
        # Prepare content data for AI (limit to avoid token limits)
        content_data = []
        for content in available_content[:30]:  # Limit for Gemini
            if request.exclude_content_ids and content.content_id in request.exclude_content_ids:
                continue
                
            content_data.append({
                "id": content.content_id,
                "type": content.content_type.value,
                "title": content.title,
                "description": content.description[:200],  # Truncate for efficiency
                "price_range": f"₹{content.price_min}-₹{content.price_max}",
                "location": content.location,
                "tags": content.tags,
                "rating": content.rating,
                "popularity": content.popularity_score
            })
        
        # Create recommendation prompt
        prompt = f"""You are an expert AI travel recommendation system. Rank travel content based on user preferences and constraints.

USER PROFILE:
- Budget: ₹{request.user_profile.budget_min:,.0f} - ₹{request.user_profile.budget_max:,.0f}
- Group Size: {request.user_profile.group_size} people
- Duration: {request.user_profile.duration_days} days
- Travel Mode: {request.user_profile.travel_mode.value}
- Travel Scope: {request.user_profile.travel_scope.value}

LEARNED PREFERENCES:
{json.dumps(user_preferences, indent=2)}

AVAILABLE CONTENT:
{json.dumps(content_data, indent=2)}

Rank ALL content by relevance considering:
1. Budget fit (strict requirement)
2. User's learned preferences from swipe patterns
3. Travel mode and group size appropriateness
4. Content quality (rating, popularity)
5. Location and feature preferences

Return a JSON array of content IDs with scores and brief explanations:
[
    {{"id": "content_id", "score": 0.95, "reason": "Perfect budget fit, matches preferred beach location and luxury features"}},
    {{"id": "content_id", "score": 0.87, "reason": "Good value for money, aligns with activity preferences"}}
]

Score range: 0.0 to 1.0. Focus on budget compatibility and preference alignment.
Return only valid JSON, no additional text."""
        
        try:
            response_content = await self._call_ai_model(prompt, temperature=0.1)
            
            # Clean and parse JSON response
            clean_response = response_content.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:-3]
            elif clean_response.startswith('```'):
                clean_response = clean_response[3:-3]
            
            rankings = json.loads(clean_response)
            
            # Map back to content objects with scores
            content_map = {c.content_id: c for c in available_content}
            recommendations = []
            
            for ranking in rankings:
                content_id = ranking.get("id")
                score = ranking.get("score", 0.0)
                
                if content_id in content_map:
                    recommendations.append((content_map[content_id], score))
            
            # Sort by score and return top results
            recommendations.sort(key=lambda x: x[1], reverse=True)
            result = recommendations[:request.batch_size]
            
            logger.info(f"Gemini generated {len(result)} recommendations for user {request.user_profile.user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendations with Gemini: {e}")
            # Fallback to simple scoring
            return self._fallback_recommendations(request, available_content)
    
    def _fallback_recommendations(self, request: RecommendationRequest, 
                                 available_content: List[TravelContent]) -> List[Tuple[TravelContent, float]]:
        """
        Fallback recommendation logic when Gemini AI fails
        """
        scored_content = []
        
        for content in available_content:
            if request.exclude_content_ids and content.content_id in request.exclude_content_ids:
                continue
                
            # Simple scoring based on budget fit and rating
            score = 0.0
            
            # Budget fit (0-0.5)
            if content.price_min <= request.user_profile.budget_max and content.price_max >= request.user_profile.budget_min:
                budget_fit = 1.0 - abs(content.price_min - request.user_profile.budget_min) / request.user_profile.budget_max
                score += budget_fit * 0.5
            
            # Rating and popularity (0-0.5)
            score += (content.rating / 5.0) * 0.3
            score += (content.popularity_score / 100.0) * 0.2
            
            scored_content.append((content, score))
        
        # Sort and return top results
        scored_content.sort(key=lambda x: x[1], reverse=True)
        return scored_content[:request.batch_size]
    
    async def predict_swipe_probability(self, user_profile: UserProfile, 
                                 content: TravelContent,
                                 swipe_history: List[SwipeInteraction]) -> float:
        """
        Predict the probability that a user will like specific content using Gemini
        
        Args:
            user_profile: User's profile and preferences
            content: Content to predict for
            swipe_history: User's historical swipe interactions
            
        Returns:
            Probability (0-1) that user will like the content
        """
        if not self.model:
            return 0.5  # Neutral fallback
        
        user_preferences = await self.analyze_user_preferences(swipe_history)
        
        prompt = f"""You are an expert at predicting user travel preferences. Based on a user's profile and swipe history, predict the probability they will like specific travel content.

USER PROFILE:
- Budget: ₹{user_profile.budget_min:,.0f} - ₹{user_profile.budget_max:,.0f}
- Group: {user_profile.group_size} people
- Duration: {user_profile.duration_days} days
- Mode: {user_profile.travel_mode.value}

LEARNED PREFERENCES:
{json.dumps(user_preferences, indent=2)}

CONTENT TO EVALUATE:
Title: {content.title}
Price: ₹{content.price_min}-₹{content.price_max}
Location: {content.location}
Tags: {content.tags}
Rating: {content.rating}

Based on budget alignment, preference patterns, and content quality, what's the probability (0.0 to 1.0) the user will like this content?

Return only a single number between 0.0 and 1.0, no additional text."""
        
        try:
            response = await self._call_ai_model(prompt, temperature=0.1)
            probability = float(response.strip())
            return max(0.0, min(1.0, probability))
        except Exception as e:
            logger.error(f"Error predicting swipe probability with Gemini: {e}")
            return 0.5
    
    async def explain_recommendation(self, user_profile: UserProfile,
                             content: TravelContent,
                             swipe_history: List[SwipeInteraction]) -> str:
        """
        Generate explanation for why content was recommended using Gemini
        
        Args:
            user_profile: User's profile and preferences
            content: Recommended content
            swipe_history: User's historical swipe interactions
            
        Returns:
            Human-readable explanation string
        """
        if not self.model:
            return "Recommended based on popularity and rating"
        
        user_preferences = await self.analyze_user_preferences(swipe_history)
        
        prompt = f"""Explain in one concise sentence why this travel content matches the user's preferences.

USER PROFILE:
- Budget: ₹{user_profile.budget_min:,.0f} - ₹{user_profile.budget_max:,.0f}
- Travel Mode: {user_profile.travel_mode.value}
- Group Size: {user_profile.group_size}

LEARNED PREFERENCES:
{json.dumps(user_preferences.get('preferences', {}), indent=2)}

RECOMMENDED CONTENT:
{content.title} - ₹{content.price_min}-₹{content.price_max} in {content.location}

Write a brief, friendly explanation focusing on the most relevant match factors.
Maximum 15 words."""
        
        try:
            response = await self._call_ai_model(prompt, temperature=0.2)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating explanation with Gemini: {e}")
            return "Matches your preferences and budget requirements"


# Demo/testing functions
def create_sample_user_profile() -> UserProfile:
    """Create a sample user profile for testing"""
    return UserProfile(
        user_id="demo_user_123",
        budget_min=50000.0,  # ₹50,000
        budget_max=150000.0,  # ₹1,50,000
        group_size=2,
        duration_days=7,
        travel_mode=TravelMode.PLEASURE,
        travel_scope=TravelScope.INDIA,
        dietary_preferences=["vegetarian"],
        transport_preferences=["flight", "train"]
    )


if __name__ == "__main__":
    # Simple test
    engine = GeminiRecommendationEngine()
    print(f"Gemini AI engine initialized: {engine.model is not None}")
    
    if engine.model:
        # Test basic functionality
        test_prompt = "Say 'Gemini AI is working!' in exactly 4 words."
        try:
            response = engine._call_ai_model(test_prompt)
            print(f"Test response: {response}")
        except Exception as e:
            print(f"Test failed: {e}")