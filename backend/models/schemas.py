"""
Pydantic schemas for API request/response models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4
from enum import Enum


# Enums (matching database enums)
class TravelMode(str, Enum):
    PLEASURE = "pleasure"
    BUSINESS = "business"
    FAMILY = "family"


class TravelScope(str, Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class SwipeAction(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class ContentType(str, Enum):
    DESTINATION = "destination"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    TRANSPORTATION = "transportation"


class GroupRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# User schemas
class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=200)
    phone_number: Optional[str] = Field(None, max_length=20)


class UserLogin(BaseModel):
    email: str
    password: str


class UserProfile(BaseSchema):
    id: UUID4
    email: str
    username: str
    full_name: Optional[str]
    phone_number: Optional[str]
    profile_image_url: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None


# User preferences schemas
class UserPreferencesCreate(BaseModel):
    default_budget_min: Optional[float] = None
    default_budget_max: Optional[float] = None
    default_group_size: Optional[int] = 1
    default_duration_days: Optional[int] = 7
    default_travel_mode: Optional[TravelMode] = TravelMode.PLEASURE
    default_travel_scope: Optional[TravelScope] = TravelScope.INDIA
    dietary_preferences: Optional[List[str]] = []
    accessibility_needs: Optional[List[str]] = []
    transport_preferences: Optional[List[str]] = []
    accommodation_preferences: Optional[List[str]] = []


class UserPreferences(BaseSchema):
    id: UUID4
    user_id: UUID4
    default_budget_min: Optional[float]
    default_budget_max: Optional[float]
    default_group_size: int
    default_duration_days: int
    default_travel_mode: TravelMode
    default_travel_scope: TravelScope
    dietary_preferences: Optional[List[str]]
    accessibility_needs: Optional[List[str]]
    transport_preferences: Optional[List[str]]
    accommodation_preferences: Optional[List[str]]
    learned_preferences: Optional[Dict[str, Any]]
    preference_confidence: float
    updated_at: datetime


# Travel content schemas
class TravelContentBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    location: str = Field(..., max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    tags: Optional[List[str]] = []
    primary_image_url: Optional[str] = None
    image_urls: Optional[List[str]] = []


class TravelContentCreate(TravelContentBase):
    content_id: str = Field(..., max_length=100)
    content_type: ContentType
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    currency: str = "INR"
    features: Optional[Dict[str, Any]] = {}


class TravelContent(BaseSchema):
    id: UUID4
    content_id: str
    content_type: ContentType
    title: str
    description: Optional[str]
    short_description: Optional[str]
    location: str
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    currency: str
    rating: Optional[float]
    review_count: int
    popularity_score: float
    primary_image_url: Optional[str]
    image_urls: Optional[List[str]]
    tags: Optional[List[str]]
    features: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime


# Swipe interaction schemas
class SwipeInteractionCreate(BaseModel):
    content_id: str  # External content ID
    action: SwipeAction
    session_id: str
    time_spent_viewing: Optional[float] = None
    swipe_velocity: Optional[float] = None
    device_type: Optional[str] = "unknown"


class SwipeInteraction(BaseSchema):
    id: UUID4
    user_id: UUID4
    content_id: UUID4
    action: SwipeAction
    session_id: str
    content_type: ContentType
    time_spent_viewing: Optional[float]
    prediction_score: Optional[float]
    explanation: Optional[str]
    timestamp: datetime


# Recommendation schemas
class RecommendationRequest(BaseModel):
    content_type: ContentType
    batch_size: int = Field(20, ge=1, le=50)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    travel_mode: Optional[TravelMode] = None
    group_size: Optional[int] = None
    duration_days: Optional[int] = None
    exclude_content_ids: Optional[List[str]] = []
    session_id: Optional[str] = None


class RecommendationItem(BaseModel):
    content: TravelContent
    relevance_score: float = Field(..., ge=0, le=1)
    explanation: Optional[str] = None
    prediction_probability: Optional[float] = None


class RecommendationResponse(BaseModel):
    items: List[RecommendationItem]
    total_available: int
    user_preferences_confidence: float
    session_id: str
    generated_at: datetime


# Group schemas
class TravelGroupCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    destination: Optional[str] = Field(None, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_total: Optional[float] = None
    max_members: int = Field(10, ge=2, le=50)
    is_public: bool = False
    requires_approval: bool = True


class TravelGroup(BaseSchema):
    id: UUID4
    name: str
    description: Optional[str]
    destination: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget_total: Optional[float]
    budget_per_person: Optional[float]
    max_members: int
    is_public: bool
    requires_approval: bool
    created_by: UUID4
    is_active: bool
    created_at: datetime
    member_count: Optional[int] = None


class GroupMember(BaseModel):
    user: UserProfile
    role: GroupRole
    joined_at: datetime


class GroupDetails(TravelGroup):
    members: List[GroupMember]
    creator: UserProfile


# Group swipe session schemas
class GroupSwipeSessionCreate(BaseModel):
    session_name: Optional[str] = None
    content_type: ContentType
    session_budget_min: Optional[float] = None
    session_budget_max: Optional[float] = None
    max_content_items: int = Field(50, ge=10, le=100)


class GroupSwipeSession(BaseSchema):
    id: UUID4
    group_id: UUID4
    session_name: Optional[str]
    content_type: ContentType
    session_budget_min: Optional[float]
    session_budget_max: Optional[float]
    max_content_items: int
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime]
    consensus_reached: bool
    final_selections: Optional[List[str]]
    conflict_items: Optional[List[str]]


class GroupSwipeVoteCreate(BaseModel):
    content_id: str  # External content ID
    action: SwipeAction
    priority_score: Optional[int] = None


class GroupSwipeVote(BaseSchema):
    id: UUID4
    session_id: UUID4
    user_id: UUID4
    content_id: UUID4
    action: SwipeAction
    vote_weight: float
    priority_score: Optional[int]
    voted_at: datetime


# Itinerary schemas
class ItineraryCreate(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    destination: str = Field(..., max_length=200)
    start_date: datetime
    end_date: datetime
    total_budget: Optional[float] = None
    travelers_count: int = Field(1, ge=1)
    group_id: Optional[UUID4] = None


class Itinerary(BaseSchema):
    id: UUID4
    user_id: UUID4
    group_id: Optional[UUID4]
    title: str
    description: Optional[str]
    destination: str
    start_date: datetime
    end_date: datetime
    duration_days: int
    total_budget: Optional[float]
    travelers_count: int
    daily_schedule: Optional[Dict[str, Any]]
    accommodations: Optional[Dict[str, Any]]
    transportation: Optional[Dict[str, Any]]
    activities: Optional[Dict[str, Any]]
    status: str
    is_shared: bool
    share_token: Optional[str]
    generated_by_ai: bool
    ai_confidence: Optional[float]
    personalization_score: Optional[float]
    created_at: datetime
    updated_at: datetime


# Analytics schemas
class AnalyticsEvent(BaseModel):
    event_type: str = Field(..., max_length=100)
    event_data: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = None
    device_type: Optional[str] = None


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[UUID4] = None


# Error schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Success schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
