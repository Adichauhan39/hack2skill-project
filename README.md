# 🌟 AI Travel Intelligence Hub

A comprehensive AI-powered travel planning platform that serves as your intelligent travel companion. This system leverages Google Gemini AI and advanced machine learning to provide personalized recommendations, smart itinerary planning, group consensus building, and creative memory creation.

## 🚀 Features

### 🤖 **AI-Powered Agents**
- **🔍 Discovery Agent**: Personalized travel recommendations using Google Gemini AI
- **📅 Itinerary Agent**: AI-generated day-by-day travel plans with themes and scheduling
- **👥 Group Agent**: Smart group decision-making and consensus building
- **💰 Budget Agent**: Intelligent budget planning and expense splitting
- **🧠 Preference Agent**: ML-powered preference learning from user interactions
- **📸 Memory Agent**: AI-created travel memory reels with creative storytelling

### 🛠 **Backend Infrastructure**
- **FastAPI REST API**: Comprehensive endpoints for all travel planning operations
- **SQLAlchemy ORM**: Robust database management with PostgreSQL support
- **Real-time AI Integration**: Live Google Gemini API calls with transparency logging
- **Swipe Intelligence**: Learn user preferences through intuitive swipe interactions

## 📋 Prerequisites

- Python 3.9+
- Google Gemini API Key
- pip package manager

## ⚡ Quick Start

### 1. Installation

```bash
git clone https://github.com/Adichauhan39/hack2skill-project.git
cd hackathon_2025
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 3. Run the AI Demo

Experience all 6 AI agents in action:
```bash
python working_ai_demo_with_interface.py
```

Then open your browser to `http://127.0.0.1:8000` for an interactive web interface.

### 4. Launch the Backend API

```bash
python -m uvicorn backend.main:app --reload
```

Access the API at `http://127.0.0.1:8000` and documentation at `http://127.0.0.1:8000/docs`

## 🎯 Usage Examples

### AI Demo Output
```
🤖 Discovery Agent - AI recommendations with real-time Gemini calls
📅 Itinerary Agent - Smart travel planning with themes
💰 Budget Agent - Per-diem calculations and expense splitting  
🧠 Preference Agent - ML learning from swipe patterns
📸 Memory Agent - Creative AI-generated travel stories
```

### API Endpoints
- `POST /recommendations` - Get AI-powered travel suggestions
- `POST /itineraries` - Generate AI itineraries  
- `POST /groups` - Create group travel consensus
- `GET /swipes` - Track preference learning
- `POST /memory-reels` - Create AI travel memories

## 🔧 Architecture

```
├── 🤖 AI Agents (Individual specialists)
│   ├── agents/
│   │   ├── discovery_agent.py    # Gemini-powered recommendations
│   │   ├── itinerary_agent.py    # AI travel planning
│   │   ├── group_agent.py        # Consensus algorithms  
│   │   ├── budget_agent.py       # Financial calculations
│   │   ├── memory_agent.py       # Creative AI content
│   │   └── base_agent.py         # Abstract base class
│
├── 🌐 Backend API
│   ├── backend/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/                 # REST endpoints
│   │   ├── models/              # Database schemas
│   │   ├── services/            # Business logic
│   │   └── agents/              # Backend agent integrations
│
└── 🎬 Demos
    └── working_ai_demo_with_interface.py   # Complete agent showcase
```

## 🧠 AI Transparency

Every AI call is logged with complete transparency:
```
🤖 [AI CALL] Sending prompt to Gemini AI...
📝 [PROMPT] Length: 2144 characters  
✅ [AI RESPONSE] Received response from Gemini AI
📊 [RESPONSE] Length: 988 characters
🎯 [AI CONFIRMED] Response successfully parsed
```

## 🔗 API Documentation

With the backend running, access interactive documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Key Endpoints
- `POST /api/recommendations` - AI-powered discovery
- `POST /api/itineraries` - AI itinerary generation  
- `POST /api/groups` - Group consensus building
- `GET /api/swipes` - Preference tracking
- `POST /api/memory-reels` - AI memory creation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful language understanding
- FastAPI for excellent API framework
- SQLAlchemy for robust ORM capabilities

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Contact: [Your Contact Information]

---
Made with ❤️ for intelligent travel planning