#!/usr/bin/env python3
"""
🌍 UNIVERSAL AI TRAVEL DEMO
Generic demonstration for any destination worldwide
Zero hardcoding - 100% dynamic user input
"""

import json
import time
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from backend.services.gemini_recommendation import GeminiRecommendationEngine

load_dotenv()

class UniversalTravelDemo:
    def __init__(self):
        self.company = "TravelAI Solutions"
        self.demo_date = datetime.now().strftime("%B %d, %Y")
        
    async def run_demo(self, auto_demo=False):
        """Universal travel demonstration"""
        
        print("\n" + "="*70)
        print(f"🌍 {self.company.upper()} - UNIVERSAL TRAVEL AI DEMO")
        print(f"📅 {self.demo_date} | Real-time AI Travel Planning")
        print("="*70)
        print("🎯 Enter ANY destination and get instant AI travel planning!")
        print("💡 Examples: Tokyo, Paris, New York, Bhilai, Dubai, etc.")
        print("-" * 70)
        
        if auto_demo:
            # Auto demo mode with predefined examples
            scenarios = [
                {
                    "destination": "Bangalore, Karnataka",
                    "budget": "premium",
                    "days": 4,
                    "interests": ["steel industry", "cultural heritage", "local cuisine"],
                    "traveler_type": "business executive"
                },
                {
                    "destination": "Kyoto, Japan",
                    "budget": "luxury", 
                    "days": 5,
                    "interests": ["temples", "traditional culture", "zen gardens"],
                    "traveler_type": "cultural enthusiast"
                }
            ]
            
            for i, scenario in enumerate(scenarios, 1):
                print(f"\n🎯 AUTO DEMO {i}/{len(scenarios)}")
                await self.demonstrate_destination(scenario)
                if i < len(scenarios):
                    print("\n⏱️ Next demo in 3 seconds...")
                    time.sleep(3)
        else:
            # Interactive mode
            destination = self.get_user_input("🌍 Enter destination", "Paris, France")
            budget = self.get_user_input("💰 Budget level (budget/premium/luxury)", "premium")
            days = self.get_user_input("📅 Number of days", "3")
            interests = self.get_user_input("🎯 Your interests (comma-separated)", "culture, food, sightseeing")
            traveler_type = self.get_user_input("👤 Traveler type", "leisure traveler")
            
            scenario = {
                "destination": destination,
                "budget": budget,
                "days": int(days) if days.isdigit() else 3,
                "interests": [interest.strip() for interest in interests.split(",")],
                "traveler_type": traveler_type
            }
            
            await self.demonstrate_destination(scenario)
    
    def get_user_input(self, prompt, default):
        """Get user input with default fallback"""
        try:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            return user_input if user_input else default
        except (EOFError, KeyboardInterrupt):
            print(f"\nUsing default: {default}")
            return default
    
    async def demonstrate_destination(self, scenario):
        """Demonstrate any destination"""
        
        print(f"\n🎯 TRAVEL PLANNING FOR: {scenario['destination'].upper()}")
        print("-" * 60)
        print(f"🌍 Destination: {scenario['destination']}")
        print(f"👤 Traveler: {scenario['traveler_type']}")
        print(f"💰 Budget: {scenario['budget']}")
        print(f"📅 Duration: {scenario['days']} days")
        print(f"🎯 Interests: {', '.join(scenario['interests'])}")
        
        # Show location info
        self.show_location_info(scenario['destination'])
        
        # AI Planning Demo  
        await self.show_ai_planning(scenario)
        
        print(f"\n✅ DEMO COMPLETE - Zero hardcoding, fully dynamic!")
        print(f"🎉 Ready for ANY destination worldwide!")
    
    def show_location_info(self, destination):
        """Show location information without API testing"""
        print(f"\n📍 DESTINATION: {destination.upper()}")
        print(f"🌍 Planning travel for: {destination}")
        print(f"🎯 Generating AI recommendations...")
    
    async def show_ai_planning(self, scenario):
        """Show Google Gemini AI planning"""
        print(f"\n🤖 GOOGLE GEMINI AI - UNIVERSAL PLANNING")
        
        try:
            ai_engine = GeminiRecommendationEngine()
            
            if not ai_engine.model:
                print("❌ Gemini AI not available")
                return
            
            # Dynamic prompt - completely generic
            prompt = f"""Create a comprehensive travel plan for a {scenario['traveler_type']} visiting {scenario['destination']}.

DESTINATION: {scenario['destination']}
DURATION: {scenario['days']} days
BUDGET: {scenario['budget']}
INTERESTS: {', '.join(scenario['interests'])}
TRAVELER TYPE: {scenario['traveler_type']}

Please provide:
1. Destination overview and highlights
2. Recommended activities based on interests
3. Daily itinerary suggestions
4. Accommodation recommendations for the budget level
5. Local food and dining suggestions
6. Transportation options
7. Cultural insights and local customs
8. Budget estimates
9. Best time to visit considerations
10. Practical tips and recommendations

Make this comprehensive, practical, and tailored to the traveler's interests and budget level."""

            print(f"🧠 AI Processing: {scenario['destination']} travel plan...")
            
            start_time = time.time()
            ai_response = await ai_engine._call_ai_model(prompt, temperature=0.4)
            end_time = time.time()
            
            processing_time = round(end_time - start_time, 2)
            
            print(f"⚡ Processing: {processing_time}s | Length: {len(ai_response)} chars")
            print(f"\n📋 AI TRAVEL PLAN:")
            print("-" * 60)
            
            # Show response with smart truncation
            lines = ai_response.split('\n')
            for i, line in enumerate(lines):
                print(line)
                if i > 0 and i % 25 == 0 and i < len(lines) - 5:
                    print(f"... [Showing first {i} lines, +{len(lines)-i} more lines available] ...")
                    break
            
            if len(lines) <= 25:
                pass  # Show all if short
            else:
                print(f"\n... [Full response: {len(lines)} total lines] ...")
            
            print("-" * 60)
            print("✅ REAL AI RESPONSE - Generated fresh for your destination!")
            
        except Exception as e:
            print(f"❌ AI Error: {str(e)}")
    
    def show_summary(self):
        """Show demo summary"""
        print(f"\n🏆 UNIVERSAL TRAVEL AI SUMMARY")
        print("="*60)
        print("✅ CAPABILITIES DEMONSTRATED:")
        print("   • Zero hardcoding - any destination")
        print("   • Live Google Gemini AI planning")
        print("   • User-driven customization")
        print("   • Dynamic content generation")
        print("   • Global destination coverage")
        
        print(f"\n🚀 PLATFORM FEATURES:")
        print("   • Universal destination support")
        print("   • Multiple budget levels")
        print("   • Customizable trip duration")
        print("   • Interest-based recommendations")
        print("   • Real-time API integration")
        
        print(f"\n🎯 READY FOR: Any travel planning scenario worldwide!")

async def main():
    """Run universal travel demonstration"""
    demo = UniversalTravelDemo()
    
    # Check for auto demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        await demo.run_demo(auto_demo=True)
    else:
        await demo.run_demo(auto_demo=False)
    
    demo.show_summary()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo ended. Thank you!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure your .env file has GOOGLE_MAPS_API_KEY and GOOGLE_API_KEY configured.")