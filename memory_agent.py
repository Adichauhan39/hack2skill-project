import google.generativeai as genai
import json
from typing import List, Dict, Optional

from base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    """
    An agent for the "AI-Generated Memory Reel" feature. It analyzes trip photos
    and itinerary to create a shareable digital souvenir.
    """

    def __init__(self, gemini_api_key: str):
        """
        Initializes the Memory Agent.

        Args:
            gemini_api_key: The Google Gemini API key for generation.
                          This agent would ideally use a multimodal model.
        """
        genai.configure(api_key=gemini_api_key)
        # For a real implementation, 'gemini-1.5-pro-vision' would be used to analyze actual images.
        # For this text-based simulation, 'gemini-1.5-flash' is sufficient.
        
        generation_config = {"response_mime_type": "application/json"}
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=generation_config
        )

    def execute(
        self,
        itinerary: Dict,
        photo_metadata: List[Dict],
        reel_style: str = "Upbeat and Fun"
    ) -> Dict:
        """
        Generates a storyboard for an AI-powered memory reel.

        Args:
            itinerary: The user's final trip itinerary.
                       e.g., {"Day 1": ["Eiffel Tower", "Louvre Museum"], ...}
            photo_metadata: A list of metadata for user's photos. In a real app,
                            this would come from a vision AI analysis.
                            e.g., [{'photo_id': 'img1.jpg', 'location': 'Eiffel Tower', 'description': 'Smiling couple in front of the Eiffel Tower', 'quality_score': 0.9}, ...]
            reel_style: The desired style of the memory reel (e.g., "Upbeat and Fun", "Cinematic", "Nostalgic").

        Returns:
            A dictionary representing the memory reel storyboard.
        """
        if not photo_metadata:
            return {"error": "No photos provided to create a memory reel."}

        prompt = self._build_prompt(itinerary, photo_metadata, reel_style)

        try:
            print("🤖 [AI CALL] Sending memory reel prompt to Gemini AI...")
            print(f"📝 [PROMPT] Style: {reel_style}, Photos: {len(photo_metadata)} items")
            response = self.model.generate_content(prompt)
            print("✅ [AI RESPONSE] Received memory reel from Gemini AI")
            print(f"📊 [RESPONSE] Length: {len(response.text)} characters")
            storyboard = self._parse_json_response(response.text)
            print("🎯 [AI CONFIRMED] Memory reel successfully parsed and formatted")
            return storyboard
        except Exception as e:
            error_message = f"Failed to generate memory reel storyboard: {e}"
            print(f"❌ [AI ERROR] Gemini API call failed: {error_message}")
            return {"error": error_message}

    def _build_prompt(
        self,
        itinerary: Dict,
        photo_metadata: List[Dict],
        reel_style: str
    ) -> str:
        """Constructs the prompt for the Gemini model."""

        itinerary_summary = json.dumps(itinerary, indent=2)
        photos_summary = json.dumps(photo_metadata, indent=2)

        json_schema_description = """
        Respond with a JSON object with a "memory_reel" key. The value should be an object with:
        - "title": A catchy title for the video (string).
        - "style": The requested style (string).
        - "music_suggestion": A suggestion for background music style (string).
        - "storyboard": A list of scenes. Each scene is an object with:
            - "day": The day of the trip (e.g., "Day 1").
            - "location": The location of the scene (string).
            - "photo_id": The ID of the selected photo (string).
            - "caption": A short, engaging caption for the scene (string).
        """

        return f"""
        You are a creative AI video editor. Your task is to create a storyboard for a short, shareable "Memory Reel" video from a user's vacation photos and itinerary.

        **Trip Itinerary:**
        {itinerary_summary}

        **Available Photos (with descriptions and quality scores from a Vision AI):**
        {photos_summary}

        **Desired Reel Style:** {reel_style}

        **Your Task:**
        Create a compelling storyboard for the memory reel.

        **Instructions:**
        1.  **Select the Best Photos:** Choose a sequence of 5-8 **unique** photos from the list. Prioritize photos with high `quality_score`.
        2.  **Variety is Key:** Ensure a wide variety of locations from the itinerary. Do not use more than one photo for the same location unless absolutely necessary to tell a compelling story.
        3.  **Create a Narrative:** Arrange the selected photos chronologically or thematically.
        4.  **Write Engaging Captions:** For each selected photo, write a short, fun, and engaging caption.
        5.  **Suggest a Title and Music:** Propose a catchy title for the reel and a suitable music style that matches the '{reel_style}' theme.
        6.  **Unique Photos Only:** Each `photo_id` in the final storyboard must be unique.
        7.  **Format the Output:** {json_schema_description}
        """

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parses the JSON response from the model."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            if response_text.strip().startswith("```json"):
                clean_response = response_text.strip()[7:-3].strip()
                return json.loads(clean_response)
            raise