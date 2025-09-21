import google.generativeai as genai
import json
from typing import List, Dict, Optional

from base_agent import BaseAgent
# Assuming data models exist, e.g., in backend.models
# from backend.models import UserProfile, Swipe

class DiscoveryAgent(BaseAgent):
    """
    A context-aware agent that learns user preferences from swipes and provides
    personalized, dynamically-optimized recommendations.
    """

    def __init__(self, api_key: str):
        """
        Initializes the Discovery Agent with the Google Gemini API key.
        """
        genai.configure(api_key=api_key)
        generation_config = {"response_mime_type": "application/json"}
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=generation_config
        )

    def execute(
        self,
        user_profile: Dict,
        swipes: List[Dict],
        context: Optional[Dict] = None,
        count: int = 10
    ) -> Dict:
        """
        Generates personalized and context-aware content recommendations.

        Args:
            user_profile: A dictionary containing user's core preferences like
                          'travel_mode', 'budget', 'scope', 'group_size'.
            swipes: A list of the user's recent swipe interactions.
            context: Optional dictionary with real-time context like 'weather',
                     'local_events', 'current_location'.
            count: The number of recommendations to generate.

        Returns:
            A dictionary containing a list of recommended content items.
        """
        prompt = self._build_prompt(user_profile, swipes, context, count)
        
        try:
            print("🤖 [AI CALL] Sending prompt to Gemini AI...")
            print(f"📝 [PROMPT] Length: {len(prompt)} characters")
            response = self.model.generate_content(prompt)
            print("✅ [AI RESPONSE] Received response from Gemini AI")
            print(f"📊 [RESPONSE] Length: {len(response.text)} characters")
            recommendations = self._parse_json_response(response.text)
            print("🎯 [AI CONFIRMED] Response successfully parsed and formatted")
            return recommendations
        except Exception as e:
            print(f"❌ [AI ERROR] Gemini API call failed: {e}")
            # Fallback to a simpler text-based generation
            return self.execute_fallback(user_profile, swipes, context, count)

    def execute_fallback(self, user_profile: Dict, swipes: List[Dict], context: Optional[Dict], count: int) -> Dict:
        """A simpler text-based fallback if JSON generation fails."""
        print("🔄 [AI FALLBACK] Switching to fallback text-based recommendation generation.")
        # Fallback to text-based generation without JSON
        text_model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = self._build_prompt(user_profile, swipes, context, count, force_text=True)
        try:
            print("🤖 [AI FALLBACK CALL] Sending fallback prompt to Gemini AI...")
            response = text_model.generate_content(prompt)
            print("✅ [AI FALLBACK RESPONSE] Received fallback response from Gemini AI")
            recommendations = self._parse_text_response(response.text)
            return {"recommendations": recommendations}
        except Exception as e:
            error_message = f"Fallback recommendation generation also failed: {e}"
            print(f"❌ [AI FALLBACK ERROR] {error_message}")
            return {"error": error_message, "recommendations": []}

    def _build_prompt(
        self,
        user_profile: Dict,
        swipes: List[Dict],
        context: Optional[Dict],
        count: int,
        force_text: bool = False
    ) -> str:
        """Constructs the prompt for the Gemini model."""
        
        liked_items = [s for s in swipes if s.get('liked')]
        disliked_items = [s for s in swipes if not s.get('liked')]
        context = context or {}

        json_schema_description = """
        Respond with a JSON object containing a single key "recommendations", which is a list of recommendation-objects.
        Each recommendation-object must have "name" (string), "category" (string, e.g., "Activity", "Hotel"), "description" (string, a brief one-liner), and "reasoning" (string, explaining why this is a good match for the user).
        """
        
        simple_text_instruction = "Provide the output as a simple numbered list of names and categories, like '1. Eiffel Tower (Activity)'. Do not repeat items the user has already swiped on."
        
        output_instruction = json_schema_description if not force_text else simple_text_instruction

        # Build context string
        context_str = ""
        if context.get('current_location'):
            context_str += f"- Current Location: {context.get('current_location')}\n"
        if context.get('weather'):
            context_str += f"- Current Weather: {context.get('weather')}\n"
        if context.get('local_events'):
            context_str += f"- Ongoing Local Events: {', '.join(context.get('local_events'))}\n"

        
        # Build liked items string
        liked_items_str = ''.join([f"  - {item.get('name', 'Item ' + str(item.get('item_id')))} ({item.get('category')})\n" for item in liked_items]) or '  - None\n'
        
        # Build disliked items string  
        disliked_items_str = ''.join([f"  - {item.get('name', 'Item ' + str(item.get('item_id')))} ({item.get('category')})\n" for item in disliked_items]) or '  - None\n'
        
        # Build context string with default
        context_display = context_str or "- No real-time context available.\n"

        prompt = f"""
        You are a world-class, context-aware AI travel discovery engine. Your task is to provide highly personalized and relevant travel recommendations.

        **User Profile:**
        - Travel Mode: {user_profile.get('travel_mode', 'Not specified')} (e.g., Business, Family, Pleasure)
        - Budget: {user_profile.get('budget', 'Not specified')} (e.g., INR/USD, budget level)
        - Scope: {user_profile.get('scope', 'Not specified')} (e.g., India, International)
        - Group Size: {user_profile.get('group_size', 1)}

        **User's Swipe History (Learned Preferences):**
        - Recent Likes:
        {liked_items_str}
        - Recent Dislikes:
        {disliked_items_str}

        **Real-time Context:**
        {context_display}

        **Your Task:**
        Based on the complete user profile, their swipe history, and the real-time context, suggest {count} new and exciting travel items.

        **Instructions:**
        1.  **Personalize:** Recommendations must align with the user's likes and avoid their dislikes.
        2.  **Contextualize:** If real-time context is available (like weather), adapt your suggestions. For example, suggest indoor activities if it's raining.
        3.  **Be Specific:** For a 'Family' mode, suggest kid-friendly places. For 'Business', suggest good restaurants for meetings or quick sightseeing spots.
        4.  **Cultural Nuance:** If the scope is 'India', incorporate India-specific cultural intelligence in your suggestions.
        5.  **Explain Yourself:** For each recommendation, provide a short 'reasoning' explaining *why* it's a good fit.
        6.  **Do Not Repeat:** Do not suggest items already present in the user's swipe history.
        7.  **Format:** {output_instruction}
        """
        return prompt

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parses the JSON response from the model."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback for markdown-wrapped JSON
            if response_text.strip().startswith("```json"):
                clean_response = response_text.strip()[7:-3].strip()
                return json.loads(clean_response)
            raise

    def _parse_text_response(self, response_text: str) -> List[Dict]:
        """Parses the fallback text response from the model into a structured list."""
        items = []
        lines = response_text.strip().split('\n')
        for line in lines:
            if '. ' in line:
                try:
                    # Simple parsing for "1. Name (Category)"
                    parts = line.split('. ', 1)
                    name_part = parts[1]
                    name = name_part
                    category = "Unknown"
                    if '(' in name_part and name_part.endswith(')'):
                        name, category = name_part[:-1].rsplit(' (', 1)
                    
                    items.append({
                        "name": name.strip(),
                        "category": category.strip(),
                        "description": "AI Recommended (Fallback)",
                        "reasoning": "Generated via fallback mechanism."
                    })
                except (IndexError, ValueError):
                    continue
        return items