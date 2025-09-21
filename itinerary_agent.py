import google.generativeai as genai
import json
from typing import List, Dict, Optional

from base_agent import BaseAgent
# from backend.services import GoogleMapsService # This would be a wrapper for Google Maps API

class ItineraryAgent(BaseAgent):
    """
    An agent that generates and optimizes a travel itinerary based on a user's
    liked items, travel pace, and other constraints, aligning with the
    "Dynamic Itinerary Pacing" feature.
    """

    def __init__(self, gemini_api_key: str, maps_api_key: str = None):
        """
        Initializes the Itinerary Agent.

        Args:
            gemini_api_key: The Google Gemini API key for generation.
            maps_api_key: The Google Maps API key for optimization. This is crucial
                          for the AI to consider travel times, though the actual
                          API calls are abstracted for this agent.
        """
        genai.configure(api_key=gemini_api_key)
        # Configure the model to expect a JSON response
        generation_config = {"response_mime_type": "application/json"}
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=generation_config
        )
        self.maps_api_key = maps_api_key
        # if self.maps_api_key:
        #     self.maps_service = GoogleMapsService(api_key=self.maps_api_key)
        #     # This service would be used to fetch real travel times, which could
        #     # be passed to the prompt for even higher accuracy.

    def execute(
        self,
        liked_items: List[Dict],
        duration_days: int,
        travel_pace: str = "Moderate",
        base_location: Optional[str] = None,
        origin_location: Optional[str] = None
    ) -> Dict:
        """
        Creates a structured, optimized itinerary.

        Args:
            liked_items: A list of content items the user has liked. Each item
                         should be a dict with 'name', 'category', and 'location'.
            duration_days: The total duration of the trip in days.
            travel_pace: The desired pace of travel ("Relaxed", "Moderate", "Packed").
            base_location: The user's primary location (e.g., hotel address) to
                           optimize travel from.
            origin_location: The user's starting city to suggest travel from.

        Returns:
            A dictionary representing the structured itinerary in JSON format.
        """
        if not liked_items:
            return {"error": "No liked items provided to create an itinerary."}

        prompt = self._build_prompt(liked_items, duration_days, travel_pace, base_location, origin_location)

        try:
            print("🤖 [AI CALL] Sending itinerary prompt to Gemini AI...")
            print(f"📝 [PROMPT] Travel pace: {travel_pace}, Duration: {duration_days} days")
            response = self.model.generate_content(prompt)
            print("✅ [AI RESPONSE] Received itinerary from Gemini AI")
            print(f"📊 [RESPONSE] Length: {len(response.text)} characters")
            itinerary = self._parse_json_response(response.text)
            print("🎯 [AI CONFIRMED] Itinerary successfully parsed and formatted")
            return itinerary
        except Exception as e:
            # This can happen if the model fails to generate valid JSON or other API errors.
            error_message = f"Failed to generate or parse itinerary: {e}"
            print(f"❌ [AI ERROR] Gemini API call failed: {error_message}")
            # Fallback to a simpler text-based generation if JSON fails
            return self.execute_fallback(liked_items, duration_days, travel_pace, base_location, origin_location)

    def execute_fallback(self, liked_items: List[Dict], duration_days: int, travel_pace: str, base_location: Optional[str], origin_location: Optional[str]) -> Dict:
        """A simpler text-based fallback if JSON generation fails."""
        print("🔄 [AI FALLBACK] Switching to fallback text-based itinerary generation.")
        # Re-initialize model for text output
        # Fallback to text-based generation without JSON
        text_model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = self._build_prompt(liked_items, duration_days, travel_pace, base_location, origin_location, force_text=True)
        try:
            response = text_model.generate_content(prompt)
            # Use the old parsing logic for the fallback
            itinerary = self._parse_text_response(response.text)
            return itinerary
        except Exception as e:
            error_message = f"Fallback itinerary generation also failed: {e}"
            print(error_message)
            return {"error": error_message}

    def _build_prompt(
        self,
        liked_items: List[Dict],
        duration_days: int,
        travel_pace: str,
        base_location: Optional[str],
        origin_location: Optional[str] = None,
        force_text: bool = False
    ) -> str:
        """Constructs the prompt for the Gemini model."""
        
        item_list = "\n".join([
            f"- Name: {item.get('name', 'N/A')}, Category: {item.get('category', 'N/A')}, Location: {item.get('location', 'N/A')}"
            for item in liked_items
        ])

        json_schema_description = """
        Respond with a JSON object. The object must have two top-level keys: "travel_suggestions" and "itinerary".
        The "travel_suggestions" object should contain a "flights" key, which is a list of 2-3 sample flight-suggestion-objects from the origin to the destination. Each flight-suggestion-object must have "airline", "flight_number", "departure_time", "arrival_time", and "price_estimate". If no origin is provided, this can be an empty list.
        The "itinerary" key must contain a list of day-objects. Each day-object should have "day" (number), "theme" (string), and "schedule" (a list of events).
        Each event in the schedule should have "time" (string, e.g., "Morning"), "activity" (string), and "description" (string).
        """

        output_instruction = json_schema_description
        if force_text:
            output_instruction = "Present the output with 'Day 1', 'Day 2', etc., as headers, listing activities for Morning, Afternoon, and Evening."

        return f"""
        You are an expert travel planner AI. Your task is to create a logical, efficient, and enjoyable itinerary based on the user's preferences.

        **Trip Details:**
        - Origin: {origin_location if origin_location else 'Not specified'}
        - Destination Area: The items are located around {base_location if base_location else 'the provided locations'}.
        - Trip Duration: {duration_days} days
        - Desired Pace: {travel_pace} (Relaxed: fewer activities, more downtime. Moderate: balanced schedule. Packed: maximize activities).
        - User's Base Location (Hotel): {base_location if base_location else 'Not specified, assume a central point.'}

        **Available Activities/Places (User's 'Liked' Items):**
        {item_list}

        **Your Instructions:**
        1.  **Suggest Flights:** If an origin location is provided, suggest 2-3 sample flights from the origin to the destination area. Include fictional but realistic airline, flight number, times, and price estimates.
        2.  **Organize Itinerary:** Create a day-by-day schedule for the {duration_days}-day trip using ONLY the items from the list above.
        3.  **Optimize for Location:** Group activities that are geographically close to each other on the same day to minimize travel time. Use the 'Location' field for each item to do this. Start and end each day considering travel to/from the base location if provided.
        4.  **Respect the Pace:** Adjust the number of activities per day based on the '{travel_pace}' pace. A 'Packed' day might have 3-4 major activities, while a 'Relaxed' day might have only 1-2 with more leisure time.
        5.  **Logical Flow:** Arrange activities in a logical order (e.g., museums in the afternoon, dinner in the evening).
        6.  **Structure the Output:** {output_instruction}
        """

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parses the JSON response from the model into a structured itinerary."""
        try:
            # The response from Gemini with response_mime_type="application/json"
            # is a clean JSON string.
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}. Response text: {response_text}")
            # Check for and clean markdown fences if they exist, as a fallback.
            if response_text.strip().startswith("```json"):
                clean_response = response_text.strip()[7:-3].strip()
                try:
                    return json.loads(clean_response)
                except json.JSONDecodeError:
                    raise # Re-raise the original error after trying to clean.
            raise  # Re-raise the exception to be caught by the execute method

    def _parse_text_response(self, response_text: str) -> Dict:
        """Parses the text response from the model into a structured itinerary (fallback)."""
        itinerary = {}
        current_day_data = []
        current_day_title = None

        def save_current_day():
            if current_day_title and current_day_data:
                itinerary[current_day_title] = current_day_data.copy()

        for line in response_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith('day '):
                save_current_day()
                current_day_title = line
                current_day_data = []
            elif current_day_title and (line.startswith('-') or '*' in line or ':' in line):
                current_day_data.append(line)
        
        save_current_day() # Save the last day
        return {"itinerary": itinerary}