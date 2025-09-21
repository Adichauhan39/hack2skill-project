# 🌟 Triplix: AI-Powered Personalized Trip Planner

> **Transforming travel planning from a time-consuming chore into an exciting, game-like discovery process**

Triplix is an intelligent, AI-powered trip planner that uses a fun, intuitive swipe-based interface to learn user preferences and generate perfectly tailored, collaborative, and instantly bookable itineraries. Reduce planning time from days to minutes while creating personalized travel experiences.

## 🎯 Project Vision

**Vision Statement:** To revolutionize travel planning by transforming it from a time-consuming chore into an exciting, game-like discovery process.

**Problem We Solve:** Modern travelers face decision fatigue, spending countless hours sifting through reviews, blogs, and booking sites to create itineraries. This fragmented process often fails to align with their unique budget, interests, and travel style.

**Our Solution:** An intelligent platform that uses swipe-based discovery, AI personalization, collaborative planning, and end-to-end booking in one seamless experience.

## ✨ Unique Features & Core Functionality

### 🎯 **Swipe-Based Discovery**
- **Visual Cards**: Beautiful images with highlights and costs for destinations, accommodations, activities, and transportation
- **Swipe Right**: Like/add to wishlist with AI learning from patterns
- **Swipe Left**: Dismiss suggestions to refine future recommendations
- **Smart Categories**: Destinations, accommodations, activities, transportation

### 🤖 **AI-Powered Agent System**
- **🔍 Discovery Agent**: Vertex AI-powered personalized recommendations using swipe pattern analysis
- **📅 Itinerary Agent**: Intelligent day-by-day travel plans with optimal routing and pacing
- **👥 Group Agent**: Collaborative planning with consensus algorithms and democratic voting
- **💰 Budget Agent**: Dynamic budget optimization with real-time expense tracking
- **🧠 Memory Agent**: AI-generated post-trip memory reels and digital souvenirs
- **� Location Intelligence Agent**: Context-aware suggestions based on real-time location

### 🌟 **Multi-Modal Planning**
- **Unified Interface**: Single swipe experience across all travel components
- **Context Intelligence**: Mode-specific recommendations (business vs. family vs. pleasure)
- **Real-time Adaptation**: Weather-aware, event-conscious suggestions
- **Cultural Intelligence**: India-specific cultural insights and recommendations

### 👥 **Group Collaboration**
- **Synchronized Swiping**: Multiple users contribute to shared wishlists in real-time
- **Consensus Algorithms**: Smart conflict resolution for group preferences
- **Democratic Voting**: Weighted decision-making for conflicting choices
- **Live Budget Tracking**: Built-in expense splitter eliminating need for separate apps

## � Target Audience & User Personas

### 🎒 **Priya, the Spontaneous Explorer (24)**
- **Profile**: Recent graduate, solo traveler, budget-conscious backpacker
- **Needs**: Quick inspiration, budget-friendly options, authentic local experiences
- **Pain Points**: Overwhelmed by generic tourist traps, difficulty finding unique experiences

### 👨‍👩‍👧‍👦 **Amit, the Family Organizer (38)**
- **Profile**: Busy professional, father planning family vacations
- **Needs**: Kid-friendly activities, family accommodations, structured plans
- **Pain Points**: Coordinating multiple people's interests and logistics stress

### 🏢 **Business Travelers & Corporate Groups**
- **Profile**: Professionals needing efficient, productive travel plans
- **Needs**: Business-friendly accommodations, meeting venues, networking opportunities
- **Pain Points**: Limited time for research, need for reliable, professional services

## 🚀 Getting Started

### �📋 Prerequisites

- Python 3.9+
- Google Gemini API Key (for AI features)
- Google Cloud Account (for Vertex AI and Firebase)
- pip package manager

### ⚡ Quick Installation

```bash
# Clone the repository
git clone https://github.com/Adichauhan39/hack2skill-project.git
cd hackathon_2025

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 🔧 Environment Configuration

Create a `.env` file with the following variables:
```env
# AI Configuration
GEMINI_API_KEY=your_google_gemini_api_key_here
VERTEX_AI_PROJECT_ID=your_vertex_ai_project_id
VERTEX_AI_REGION=us-central1

# Database Configuration
DATABASE_URL=sqlite:///./tripplanner.db

# External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

### 🎮 Experience the AI Demo

Run the comprehensive AI agent demonstration:
```bash
python working_ai_demo_with_interface.py
```

This showcases all 6 AI agents working together to create a complete travel planning experience.

### 🌐 Launch the Backend API

```bash
# Start the FastAPI backend
python -m uvicorn backend.main:app --reload

# Access the application
# Web Interface: http://127.0.0.1:8000
# API Documentation: http://127.0.0.1:8000/docs
# Alternative Docs: http://127.0.0.1:8000/redoc
```

## 🏗️ System Architecture & Technology Stack

### 🎯 **High-Level Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flutter App   │────│   Backend API    │────│  AI/ML Engine   │
│  (Mobile/Web)   │    │   (FastAPI)      │    │  (Vertex AI)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Firebase      │    │   Google Cloud   │    │   BigQuery      │
│  (Auth/Sync)    │    │   (Compute)      │    │  (Analytics)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 💻 **Technology Stack**

#### **Frontend (Planned)**
- **Flutter**: Cross-platform mobile application
- **Redux/Riverpod**: State management for complex user interactions
- **Custom Swipe Components**: Built with GestureDetector and Reanimated
- **Google Maps Integration**: Interactive maps and location services

#### **Backend (Current Implementation)**
- **FastAPI**: High-performance REST API with automatic documentation
- **SQLAlchemy ORM**: Database abstraction with PostgreSQL/SQLite support
- **Firebase**: Authentication and real-time synchronization
- **Google Cloud Run**: Serverless deployment for scalability

#### **AI/ML Pipeline**
- **Google Vertex AI**: Machine learning model hosting and inference
- **Google Gemini AI**: Natural language processing and recommendations
- **Vertex AI Matching Engine**: Collaborative filtering for recommendations
- **BigQuery**: Data warehousing for model training and analytics

#### **External Integrations**
- **Google Maps APIs**: Places, Distance Matrix, Geocoding
- **Booking Partners**: Flight/hotel/activity booking integrations
- **Payment Gateway**: Stripe/Razorpay for secure transactions

### � **Project Structure**

```
triplix/
├── 🤖 AI Agents Core
│   ├── agents/
│   │   ├── discovery_agent.py      # Vertex AI recommendations
│   │   ├── itinerary_agent.py      # Intelligent trip planning
│   │   ├── group_agent.py          # Collaborative decision making
│   │   ├── budget_agent.py         # Financial optimization
│   │   ├── memory_agent.py         # Post-trip content creation
│   │   └── base_agent.py           # Abstract agent framework
│   │
├── 🌐 Backend Infrastructure
│   ├── backend/
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── api/                    # REST API endpoints
│   │   │   ├── recommendations.py  # Discovery endpoints
│   │   │   ├── itineraries.py      # Planning endpoints
│   │   │   ├── groups.py           # Collaboration endpoints
│   │   │   ├── swipes.py           # Preference learning
│   │   │   └── auth.py             # Authentication
│   │   ├── models/                 # Database schemas
│   │   │   ├── database.py         # Database configuration
│   │   │   ├── schemas.py          # Pydantic models
│   │   │   └── db_config.py        # Connection management
│   │   ├── agents/                 # Backend agent integrations
│   │   └── utils/                  # Utility functions
│   │
├── 📊 Data & Analytics
│   ├── seed_database.py            # Initial data seeding
│   ├── tripplanner.db              # SQLite database
│   └── logs/                       # Application logs
│
├── 🎬 Demonstrations
│   ├── working_ai_demo_with_interface.py  # Complete demo
│   └── AI_SETUP_GUIDE.md          # Setup instructions
│
└── 📋 Configuration
    ├── requirements.txt            # Python dependencies
    ├── .env.example               # Environment template
    └── README.md                  # This file
```

## 🚀 Usage Examples & API Reference

### 🎮 **AI Demo Experience**

When you run the demo, you'll experience:
```
🤖 Discovery Agent    → AI-powered destination recommendations
📅 Itinerary Agent    → Smart day-by-day travel planning
👥 Group Agent        → Collaborative decision-making algorithms
💰 Budget Agent       → Dynamic budget optimization
🧠 Preference Agent   → Machine learning from user interactions
📸 Memory Agent       → AI-generated travel storytelling
```

### 📡 **Core API Endpoints**

#### **Discovery & Recommendations**
```http
POST /api/recommendations
Content-Type: application/json

{
  "budget": 50000,
  "group_size": 2,
  "duration": 7,
  "mode": "Pleasure",
  "scope": "India",
  "preferences": {
    "accommodation": "hotel",
    "transport": "flight",
    "activities": ["culture", "food", "nature"]
  }
}
```

#### **Itinerary Generation**
```http
POST /api/itineraries
Content-Type: application/json

{
  "destination": "Goa",
  "duration": 5,
  "budget_per_day": 5000,
  "group_preferences": ["beach", "nightlife", "heritage"],
  "pace": "moderate"
}
```

#### **Group Collaboration**
```http
POST /api/groups
Content-Type: application/json

{
  "group_name": "Goa Trip 2025",
  "members": ["user1@email.com", "user2@email.com"],
  "trip_parameters": {
    "destination": "Goa",
    "budget": 100000,
    "duration": 7
  }
}
```

#### **Swipe Learning**
```http
POST /api/swipes
Content-Type: application/json

{
  "user_id": "user123",
  "item_id": "destination_goa",
  "action": "like",
  "item_type": "destination",
  "context": {
    "budget_range": "medium",
    "travel_mode": "leisure"
  }
}
```

### 🎯 **Example Responses**

#### **Discovery Agent Response**
```json
{
  "recommendations": [
    {
      "type": "destination",
      "name": "Udaipur, Rajasthan",
      "score": 0.95,
      "estimated_cost": 25000,
      "highlights": ["Lake Palace", "City Palace", "Boat rides"],
      "why_recommended": "Perfect blend of culture and romance within budget"
    }
  ],
  "learning_insights": {
    "preferred_categories": ["heritage", "lakes", "luxury"],
    "budget_comfort": "mid-range",
    "group_dynamics": "romantic_couple"
  }
}
```

## 🔍 **Advanced Features & Future Roadmap**

### 🎯 **V1 Core Features (Current)**
- ✅ Swipe-based discovery interface
- ✅ AI-powered recommendation engine
- ✅ Group collaboration tools
- ✅ Budget optimization
- ✅ Real-time preference learning

### 🚀 **V2 Roadmap (Planned)**

#### **1. Dynamic Itinerary Pacing**
- **Smart Scheduling**: AI optimizes daily activities based on travel pace preference
- **Route Optimization**: Google Maps integration for efficient travel routes
- **Pace Customization**: Relaxed, Moderate, or Packed travel styles

#### **2. Live Budget Tracker & Expense Splitter**
- **Real-time Tracking**: Live expense monitoring during trips
- **Group Splitting**: Built-in expense sharing for group travel
- **Budget Alerts**: Smart notifications for budget optimization

#### **3. Hyper-Local Discovery Mode**
- **Location-Aware**: Real-time suggestions based on current location
- **Context Intelligence**: Weather, events, and local happenings integration
- **Spontaneous Discovery**: Serendipitous local experience recommendations

#### **4. AI-Generated Memory Reels**
- **Automatic Creation**: Post-trip memory compilation using photos and itinerary
- **Creative Storytelling**: AI-generated travel narratives and video montages
- **Social Sharing**: Easy sharing of beautiful travel memories

## 📈 **Market Validation & Competitive Advantage**

### 🎯 **Market Gap Analysis**
- **Problem**: Existing travel apps are siloed (TripAdvisor for reviews, Skyscanner for booking, TripIt for organization)
- **Our Solution**: First platform to integrate **gamified discovery + AI personalization + collaborative planning + end-to-end booking**

### 🏆 **Competitive Differentiation**
- **Direct Competitors**: Laika Travel, Swipe Cities (limited scope, no booking integration)
- **Indirect Competitors**: Wanderlog, Kayak, Expedia (weak on personalized discovery)
- **Our USP**: Only travel app that transforms planning into a collaborative game with intelligent, bookable outcomes

### 💰 **Monetization Strategy**

#### **Phase 1: Launch (Current)**
- **Affiliate Commissions**: Revenue from booking partners (flights, hotels, activities)
- **Zero User Cost**: All core features free to accelerate adoption

#### **Phase 2: Growth (Planned)**
- **Freemium Model**: 
  - **Free Tier**: Core functionality with limited trips, ad-supported
  - **Premium Tier**: Advanced V2 features, unlimited trips, ad-free experience

## 🛠️ **Development & Deployment**

### 🔧 **Local Development**

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
python -m pytest tests/ -v

# Code formatting
black .
isort .

# Type checking
mypy .

# Start development server with hot reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 🌐 **Production Deployment**

#### **Google Cloud Deployment**
```bash
# Deploy to Cloud Run
gcloud run deploy triplix-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Set up Cloud SQL for production database
gcloud sql instances create triplix-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1
```

#### **Docker Deployment**
```bash
# Build Docker image
docker build -t triplix-api .

# Run locally with Docker
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key triplix-api

# Deploy to any cloud provider
docker push your-registry/triplix-api:latest
```

### � **Monitoring & Analytics**

- **Application Logs**: Comprehensive logging in `logs/app.log`
- **AI Transparency**: Every AI call logged with full prompt/response details
- **Performance Metrics**: API response times, error rates, user engagement
- **Business Metrics**: Conversion rates, booking success, user retention

## 🧠 **AI Transparency & Ethics**

### 🔍 **Complete AI Visibility**
Every AI interaction is logged with full transparency:
```
🤖 [AI CALL] Sending prompt to Gemini AI...
📝 [PROMPT] Length: 2144 characters  
✅ [AI RESPONSE] Received response from Gemini AI
📊 [RESPONSE] Length: 988 characters
🎯 [AI CONFIRMED] Response successfully parsed
```

### 🛡️ **Ethical AI Principles**
- **User Privacy**: All personal data encrypted and never shared with AI providers
- **Bias Prevention**: Regular model auditing for fair recommendations across demographics
- **Transparency**: Users always know when interacting with AI vs. human-curated content
- **Control**: Users can always override AI suggestions and customize preferences

## 🤝 **Contributing**

We welcome contributions from the community! Here's how you can get involved:

### �️ **Development Workflow**
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/hack2skill-project.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes with proper testing
5. **Commit** with descriptive messages: `git commit -m 'Add: Implement swipe gesture optimization'`
6. **Push** to your branch: `git push origin feature/amazing-feature`
7. **Create** a Pull Request with detailed description

### 🎯 **Contribution Areas**
- **🤖 AI Agents**: Improve recommendation algorithms and learning models
- **🎨 Frontend**: Flutter UI components and swipe interactions
- **🔧 Backend**: API optimization and new endpoint development
- **📊 Analytics**: User behavior tracking and business intelligence
- **📱 Mobile**: Cross-platform mobile app development
- **🧪 Testing**: Unit tests, integration tests, and user acceptance testing

### 📋 **Code Standards**
- Follow PEP 8 for Python code
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 80%
- Document API endpoints with proper examples

## 🏆 **Success Metrics & KPIs**

### 📊 **User Engagement**
- **Daily Active Users (DAU)**: Target engagement and retention
- **Swipes per Session**: Average user interaction depth
- **Session Duration**: Time spent in discovery and planning

### 💰 **Business Metrics**
- **Itinerary Creation Rate**: % of users who complete trip planning
- **Booking Conversion Rate**: % of itineraries resulting in bookings
- **Revenue per User**: Average booking commission generated
- **Group Collaboration Rate**: % of trips planned collaboratively

### 🎯 **Technical Performance**
- **API Response Time**: <200ms for 95% of requests
- **AI Recommendation Accuracy**: User satisfaction with suggestions
- **System Uptime**: 99.9% availability target

## 📄 **License & Legal**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### 🔒 **Privacy & Data Protection**
- GDPR compliant data handling
- User data encryption at rest and in transit
- Minimal data collection with explicit consent
- Right to data deletion and portability

## 🙏 **Acknowledgments**

### 🤖 **AI & Technology Partners**
- **Google Gemini AI** - Advanced language understanding and generation
- **Google Vertex AI** - Machine learning model hosting and inference
- **Google Cloud Platform** - Scalable cloud infrastructure
- **FastAPI** - High-performance API framework
- **SQLAlchemy** - Robust database ORM

### 🏆 **Special Recognition**
- **Hack2Skill Hackathon 2025** - Platform for innovation
- **Open Source Community** - Inspiration and collaboration
- **Beta Testers** - Early feedback and validation

## 📞 **Support & Community**

### 🆘 **Getting Help**
- **GitHub Issues**: [Create an issue](https://github.com/Adichauhan39/hack2skill-project/issues) for bugs or feature requests
- **Discussions**: Join our [GitHub Discussions](https://github.com/Adichauhan39/hack2skill-project/discussions) for general questions
- **Documentation**: Check our comprehensive docs and API reference

### 📧 **Contact Information**
- **Project Lead**: [Aditya Chauhan](https://github.com/Adichauhan39)
- **Email**: support@triplix.ai (coming soon)
- **Twitter**: [@TriplixAI](https://twitter.com/TriplixAI) (coming soon)

### 🌟 **Community Guidelines**
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Contribute to a positive environment

---

## 🚀 **Ready to Transform Travel Planning?**

**Triplix** is more than just another travel app - it's a complete reimagining of how people discover, plan, and experience travel. By combining the addictive engagement of swipe-based interfaces with the intelligence of AI and the power of collaborative planning, we're creating the future of travel.

### 🎯 **Join Our Mission**
- **Developers**: Contribute to cutting-edge AI and mobile development
- **Travelers**: Help us test and refine the ultimate planning experience  
- **Partners**: Collaborate with us to revolutionize the travel industry
- **Investors**: Be part of the next big transformation in travel tech

---

<div align="center">

**Made with ❤️ for the future of intelligent travel planning**

[🌟 Star this repository](https://github.com/Adichauhan39/hack2skill-project) | [🍴 Fork and contribute](https://github.com/Adichauhan39/hack2skill-project/fork) | [📧 Join our community](mailto:support@triplix.ai)

**✈️ Happy Travels! 🌍**

</div>