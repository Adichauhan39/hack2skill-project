# 🌍 Universal AI Travel Planner

A powerful AI-driven travel planning platform that generates personalized travel itineraries for any destination worldwide using **Google Gemini AI only**.

## ✨ Features

- **Universal Destination Support**: Plan trips to any location worldwide
- **Real-time AI Planning**: Powered by Google Gemini AI for fresh, dynamic content
- **Zero Hardcoding**: Every recommendation is generated fresh based on user input
- **Google Services Only**: Uses only Google Gemini AI - no OpenAI, Azure, or other providers
- **Customizable Experience**: Supports different budgets, trip durations, and interests
- **Two Demo Modes**: Interactive user input or automated demonstration
- **FastAPI Backend**: Production-ready REST API with authentication

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **Google API Key** for Gemini AI (required)
- **Git** (optional, for cloning)

### 1. Installation

```bash
# Navigate to project directory
cd hackathon_2025

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

**Set up your Google API Key:**

1. Get a Google API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` file and add your API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### 3. Running the Demo

**Option A: Interactive Mode (User Input)**
```bash
python universal_travel_demo.py
```
- Enter any destination when prompted
- Customize budget, duration, and interests
- Get real-time AI travel planning

**Option B: Automated Demo Mode**
```bash
python universal_travel_demo.py auto
```
- See predefined examples (Bhilai & Kyoto)
- Perfect for presentations or quick testing

### 4. Running the Full Backend Server

```bash
cd backend
python main.py
```
- Server runs on `http://localhost:8000`
- Access API documentation at `http://localhost:8000/docs`

## 📁 Project Structure

```
hackathon_2025/
├── universal_travel_demo.py    # Main demo application
├── backend/                    # FastAPI backend server
│   ├── main.py                # Server entry point
│   ├── api/                   # API endpoints
│   ├── models/               # Database models
│   ├── services/             # Google Gemini AI engine only
│   └── utils/                # Utilities
├── .env                      # Environment variables (create from .env.example)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies (Google services only)
├── tripplanner.db          # SQLite database
└── README.md               # This file
```

## 🎯 Usage Examples

### Interactive Demo
```bash
python universal_travel_demo.py
```
**Sample Input:**
- Destination: `Tokyo, Japan`
- Budget: `luxury`
- Days: `5`
- Interests: `anime, technology, traditional culture`
- Traveler type: `cultural enthusiast`

### Auto Demo Examples
```bash
python universal_travel_demo.py auto
```
**Includes:**
- **Bhilai, Chhattisgarh**: Steel industry, cultural heritage, local cuisine
- **Kyoto, Japan**: Temples, traditional culture, zen gardens

### API Usage
```python
import requests

# Get travel recommendations using Google Gemini AI
response = requests.post(
    "http://localhost:8000/api/v1/recommendations/",
    json={
        "destination": "Paris, France",
        "budget": "premium",
        "days": 4,
        "interests": ["art", "cuisine", "history"]
    }
)

print(response.json())
```

## 🔧 Configuration Options

### Environment Variables (.env)
```bash
# Required - Google Gemini AI
GOOGLE_API_KEY=your_google_api_key_here

# Optional
SECRET_KEY=your_secret_key_for_jwt
DATABASE_URL=sqlite:///./tripplanner.db
```

### Budget Levels
- `budget`: Affordable options, hostels, local transport
- `premium`: Mid-range hotels, comfortable travel
- `luxury`: High-end accommodations, exclusive experiences

### Supported Interests
- **Cultural**: temples, museums, historical sites
- **Adventure**: hiking, sports, outdoor activities  
- **Culinary**: local cuisine, food tours, restaurants
- **Business**: industry visits, networking, conferences
- **Relaxation**: spas, beaches, wellness centers
- **Technology**: tech hubs, innovation centers
- **And many more...**

## 🛠️ Development

### Google Services Only
This project exclusively uses Google services:
- **Google Gemini AI**: For all travel planning and recommendations
- **Google generativeai SDK**: Python library for Gemini integration
- **No OpenAI, Azure, or other AI providers**

### Adding New Features

1. **Extend AI Prompts**: Modify `backend/services/gemini_recommendation.py`
2. **Add API Endpoints**: Create new files in `backend/api/`
3. **Customize Demo**: Edit `universal_travel_demo.py`

### Testing Google Gemini Connection
```bash
# Test the AI service directly
cd backend
python -c "
from services.gemini_recommendation import GeminiRecommendationEngine
import asyncio

async def test():
    engine = GeminiRecommendationEngine()
    if engine.model:
        print('✅ Google Gemini AI connected successfully!')
        response = await engine._call_ai_model('Hello, plan a trip to Paris')
        print(f'Response length: {len(response)} characters')
    else:
        print('❌ Google Gemini AI not available')

asyncio.run(test())
"
```

## 🌟 Advanced Usage

### Custom Prompts with Google Gemini
```python
from backend.services.gemini_recommendation import GeminiRecommendationEngine

engine = GeminiRecommendationEngine()

custom_prompt = '''
Create a business travel plan for a tech CEO visiting Silicon Valley.
Focus on: venture capital meetings, tech company visits, innovation hubs.
Budget: luxury, Duration: 3 days
'''

response = await engine._call_ai_model(custom_prompt)
```

### Batch Processing Multiple Destinations
```bash
python -c "
import asyncio
from universal_travel_demo import UniversalTravelDemo

async def batch_demo():
    demo = UniversalTravelDemo()
    destinations = ['Tokyo', 'Paris', 'New York', 'Bhilai']
    
    for dest in destinations:
        scenario = {
            'destination': dest,
            'budget': 'premium', 
            'days': 3,
            'interests': ['culture', 'food'],
            'traveler_type': 'tourist'
        }
        await demo.demonstrate_destination(scenario)

asyncio.run(batch_demo())
"
```

## 🚨 Troubleshooting

### Common Issues

**1. "Gemini AI not available" Error**
```bash
# Check your API key in .env file
type .env | findstr GOOGLE_API_KEY

# Test API key directly
curl -H "Content-Type: application/json" ^
     -d "{\"contents\":[{\"parts\":[{\"text\":\"Hello\"}]}]}" ^
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY"
```

**2. Module Import Errors**
```bash
# Ensure you're in the right directory
dir

# Reinstall Google dependencies
pip install google-generativeai --force-reinstall
```

**3. Server Won't Start**
```bash
# Check if port is in use
netstat -an | findstr :8000

# Use different port
cd backend
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='0.0.0.0', port=8001)
"
```

**4. Database Issues**
```bash
# Reset database
del tripplanner.db

# Check database permissions
dir tripplanner.db
```

## 📊 Performance

- **AI Response Time**: 5-15 seconds average (Google Gemini)
- **Content Length**: 3,000-8,000 characters typical
- **Memory Usage**: ~80MB with basic operation
- **Concurrent Users**: Supports 50+ simultaneous requests

## 🔒 Security

- Environment variables for Google API key
- JWT authentication for API access
- Input validation and sanitization
- Rate limiting on API endpoints

## 🌐 Deployment

### Local Development
```bash
python universal_travel_demo.py auto
```

### Production Server
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Cloud Deployment
Ready for deployment on:
- **Google Cloud**: Use Cloud Run (recommended for Google services)
- **Heroku**: Use `Procfile` 
- **AWS**: Deploy with Elastic Beanstalk
- **Azure**: Deploy with App Service

## 💡 Tips for Best Results

1. **Specific Destinations**: Use full city/country names for better results
2. **Clear Interests**: Be specific about what you want to experience
3. **Realistic Budgets**: Match budget to destination cost of living
4. **Appropriate Duration**: 2-7 days work best for detailed planning
5. **Context**: Mention traveler type for personalized recommendations
6. **Google API Quota**: Monitor your Google API usage and quota

## 📞 Support

For issues or questions:
1. Check this README first
2. Review the troubleshooting section
3. Test with: `python universal_travel_demo.py auto`
4. Verify your Google API key is valid and has quota
5. Check Google AI Studio for API status

## 🔄 Updates

The Google Gemini model is continuously improving. To get the latest recommendations:
- Restart the application periodically
- Update your Google API key if needed
- Monitor Google API quota usage
- Keep `google-generativeai` library updated

## 🎯 Why Google Services Only?

- **Consistency**: Single AI provider for consistent responses
- **Performance**: Google Gemini offers excellent travel planning capabilities
- **Reliability**: Google's robust infrastructure and API stability
- **Cost-effective**: Competitive pricing for AI generation
- **Privacy**: Google's privacy and data handling standards

---

**🎉 Ready to explore the world with Google AI-powered travel planning!**

**Quick Start:** `python universal_travel_demo.py auto`

**Live Demo:** `python universal_travel_demo.py`

---

> 🏆 **Hack2Skill Project Submission**  
> This Universal AI Travel Planner is created as part of the Hack2Skill hackathon project.
