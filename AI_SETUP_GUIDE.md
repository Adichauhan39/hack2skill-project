# 🚀 AI Travel Intelligence Setup Guide

## 🎯 Quick Start: Get Your AI System Running in 5 Minutes

### Step 1: Environment Setup
```bash
# Copy the environment template
cp .env.example .env
```

### Step 2: Get Google Gemini API Key (REQUIRED)

#### 🤖 Google Gemini AI Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key" 
3. Copy your key and update `.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_key_here
   ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the AI Demo
```bash
python working_ai_demo.py
```

## 🎉 Expected Output
You should see all 6 AI agents working with full transparency:
```
🤖 Discovery Agent - AI recommendations with real-time Gemini calls
📅 Itinerary Agent - Smart travel planning with themes  
💰 Budget Agent - Per-diem calculations and expense splitting
🧠 Preference Agent - ML learning from swipe patterns
📸 Memory Agent - Creative AI-generated travel stories
👥 Group Agent - Consensus building algorithms
```

Each AI call shows transparent logging:
```
🤖 [AI CALL] Sending prompt to Gemini AI...
📝 [PROMPT] Length: 2144 characters
✅ [AI RESPONSE] Received response from Gemini AI
📊 [RESPONSE] Length: 988 characters
🎯 [AI CONFIRMED] Response successfully parsed
```

## 🔧 Optional: Backend API Setup

### Database Configuration
For full backend functionality, set up PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
```

Or use SQLite for development:
```env
DATABASE_URL=sqlite:///./tripplanner.db
```

### Launch API Server
```bash
python -m uvicorn backend.main:app --reload
```

Access API documentation at: `http://127.0.0.1:8000/docs`

## 🌟 Available AI Features

### 🤖 **Discovery Agent**
- Real-time Google Gemini AI recommendations
- Personalized travel suggestions
- Context-aware content generation

### 📅 **Itinerary Agent** 
- AI-powered day-by-day planning
- Theme-based itinerary creation
- Smart scheduling optimization

### 💰 **Budget Agent**
- Intelligent per-diem calculations
- Group expense splitting
- Financial planning algorithms

### 🧠 **Preference Agent**
- Machine learning from swipe data
- Dynamic preference modeling
- Confidence-based recommendations

### 📸 **Memory Agent**
- AI-generated travel memory reels
- Creative storytelling with photos
- Personalized narrative creation

### 👥 **Group Agent**
- Democratic consensus algorithms
- Voting and preference aggregation
- Conflict resolution for group travel

## 🔗 API Endpoints

### Core AI Endpoints:
- `POST /api/recommendations` - AI-powered discovery
- `POST /api/itineraries` - AI itinerary generation
- `POST /api/groups` - Group consensus building
- `GET /api/swipes` - Preference tracking
- `POST /api/memory-reels` - AI memory creation

### Health & Status:
- `GET /health` - System health check
- `GET /api/status` - AI service status

## 🚨 Troubleshooting

### Common Issues:

**Import Errors:**
```bash
pip install -r requirements.txt
python -c "import google.generativeai; print('Gemini AI ready!')"
```

**API Key Issues:**
- Check `.env` file exists and has correct format
- Verify key validity at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Ensure no extra spaces in the key

**Demo Not Working:**
```bash
# Test basic functionality
python -c "import discovery_agent; print('Agents loaded successfully!')"
```

**Permission Errors:**
- Check file permissions on `.env`
- Verify Python virtual environment is activated

### Debug Mode:
Set in `.env` for detailed logging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📞 Support

For issues or questions:
- Check demo output for error messages
- Verify all dependencies are installed
- Ensure Gemini API key is valid

---

🎊 **Your AI Travel Intelligence Hub is ready to revolutionize travel planning!**