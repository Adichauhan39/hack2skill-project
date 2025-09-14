"""
Database models for AI-powered trip planner

Uses SQLAlchemy for ORM with PostgreSQL database.
Models include users, preferences, travel content, swipe interactions, and group collaboration.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, 
    ForeignKey, Table, JSON, Enum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid


Base = declarative_base()


# Enums
class TravelModeEnum(PyEnum):
    PLEASURE = "pleasure"
    BUSINESS = "business"
    FAMILY = "family"


class TravelScopeEnum(PyEnum):
    INDIA = "india"
    INTERNATIONAL = "international"


class SwipeActionEnum(PyEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class ContentTypeEnum(PyEnum):
    DESTINATION = "destination"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    TRANSPORTATION = "transportation"


class GroupRoleEnum(PyEnum):
    ADMIN = "admin"
    MEMBER = "member"


class BookingStatusEnum(PyEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


# Association tables for many-to-many relationships
user_group_association = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('group_id', UUID(as_uuid=True), ForeignKey('travel_groups.id'), primary_key=True),
    Column('role', Enum(GroupRoleEnum), default=GroupRoleEnum.MEMBER),
    Column('joined_at', DateTime, default=datetime.utcnow)
)


class User(Base):
    """User accounts and profiles"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    phone_number = Column(String(20))
    date_of_birth = Column(DateTime)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile info
    profile_image_url = Column(String(500))
    bio = Column(Text)
    location = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    swipe_interactions = relationship("SwipeInteraction", back_populates="user")
    travel_groups = relationship("TravelGroup", secondary=user_group_association, back_populates="users")
    created_groups = relationship("TravelGroup", foreign_keys="TravelGroup.created_by")
    itineraries = relationship("Itinerary", back_populates="user")


class UserPreference(Base):
    """User travel preferences and learned patterns"""
    __tablename__ = 'user_preferences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    
    # Default preferences
    default_budget_min = Column(Float)
    default_budget_max = Column(Float)
    default_group_size = Column(Integer, default=1)
    default_duration_days = Column(Integer, default=7)
    default_travel_mode = Column(Enum(TravelModeEnum), default=TravelModeEnum.PLEASURE)
    default_travel_scope = Column(Enum(TravelScopeEnum), default=TravelScopeEnum.INDIA)
    
    # Personal preferences
    dietary_preferences = Column(JSON)  # ["vegetarian", "vegan", "gluten-free"]
    accessibility_needs = Column(JSON)  # ["wheelchair", "hearing_impaired"]
    transport_preferences = Column(JSON)  # ["flight", "train", "bus", "car"]
    accommodation_preferences = Column(JSON)  # ["hotel", "hostel", "resort", "homestay"]
    
    # AI learned preferences
    learned_preferences = Column(JSON)  # AI-extracted preferences from swipe patterns
    preference_confidence = Column(Float, default=0.0)  # 0-1 confidence in learned preferences
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class TravelContent(Base):
    """Swipeable travel content (destinations, accommodations, activities, etc.)"""
    __tablename__ = 'travel_content'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(100), unique=True, nullable=False, index=True)  # External ID
    content_type = Column(Enum(ContentTypeEnum), nullable=False, index=True)
    
    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Location
    location = Column(String(200), nullable=False, index=True)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True) 
    country = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Pricing
    price_min = Column(Float)
    price_max = Column(Float)
    currency = Column(String(3), default="INR")
    price_per_person = Column(Boolean, default=True)
    
    # Content quality
    rating = Column(Float)  # 0-5 star rating
    review_count = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)  # 0-100 popularity
    
    # Media
    primary_image_url = Column(String(500))
    image_urls = Column(JSON)  # Array of image URLs
    video_url = Column(String(500))
    
    # Metadata
    tags = Column(JSON)  # ["beach", "adventure", "family-friendly"]
    features = Column(JSON)  # Content-specific features
    availability_info = Column(JSON)  # Seasonal, booking info, etc.
    
    # SEO and content
    seo_keywords = Column(JSON)
    external_links = Column(JSON)  # Links to booking sites, official pages
    
    # Admin
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_by = Column(String(100))  # Data source identifier
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    swipe_interactions = relationship("SwipeInteraction", back_populates="content")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_type_location', 'content_type', 'location'),
        Index('idx_price_range', 'price_min', 'price_max'),
        Index('idx_rating_popularity', 'rating', 'popularity_score'),
    )


class SwipeInteraction(Base):
    """Records user swipe interactions for learning preferences"""
    __tablename__ = 'swipe_interactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('travel_content.id'), nullable=False, index=True)
    
    # Swipe data
    action = Column(Enum(SwipeActionEnum), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)  # Group swipes by session
    
    # Context
    content_type = Column(Enum(ContentTypeEnum), nullable=False)
    user_budget_min = Column(Float)  # User's budget at time of swipe
    user_budget_max = Column(Float)
    travel_mode = Column(Enum(TravelModeEnum))
    group_size = Column(Integer)
    
    # Interaction metadata
    time_spent_viewing = Column(Float)  # Seconds spent viewing content
    swipe_velocity = Column(Float)  # Speed of swipe (fast = less consideration)
    device_type = Column(String(50))  # mobile, tablet, desktop
    
    # AI analysis
    prediction_score = Column(Float)  # AI's predicted like probability before swipe
    explanation = Column(Text)  # Why this was recommended
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="swipe_interactions")
    content = relationship("TravelContent", back_populates="swipe_interactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_session', 'user_id', 'session_id'),
        Index('idx_user_action_timestamp', 'user_id', 'action', 'timestamp'),
    )


class TravelGroup(Base):
    """Groups for collaborative trip planning"""
    __tablename__ = 'travel_groups'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Trip details
    destination = Column(String(200))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget_total = Column(Float)
    budget_per_person = Column(Float)
    
    # Settings
    max_members = Column(Integer, default=10)
    is_public = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    
    # Group dynamics
    decision_method = Column(String(50), default="majority")  # majority, consensus, admin
    voting_threshold = Column(Float, default=0.6)  # 60% for majority
    
    # Admin
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_group_association, back_populates="travel_groups")
    creator = relationship("User", foreign_keys=[created_by])
    group_swipes = relationship("GroupSwipeSession", back_populates="group")
    itineraries = relationship("Itinerary", back_populates="group")


class GroupSwipeSession(Base):
    """Synchronized swipe sessions for groups"""
    __tablename__ = 'group_swipe_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey('travel_groups.id'), nullable=False)
    session_name = Column(String(200))
    
    # Session configuration  
    content_type = Column(Enum(ContentTypeEnum), nullable=False)
    session_budget_min = Column(Float)
    session_budget_max = Column(Float)
    max_content_items = Column(Integer, default=50)
    
    # Status
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Results
    consensus_reached = Column(Boolean, default=False)
    final_selections = Column(JSON)  # Content IDs that reached consensus
    conflict_items = Column(JSON)  # Content IDs with conflicting votes
    
    # Relationships
    group = relationship("TravelGroup", back_populates="group_swipes")
    votes = relationship("GroupSwipeVote", back_populates="session")


class GroupSwipeVote(Base):
    """Individual votes within group swipe sessions"""
    __tablename__ = 'group_swipe_votes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('group_swipe_sessions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content_id = Column(UUID(as_uuid=True), ForeignKey('travel_content.id'), nullable=False)
    
    # Vote data
    action = Column(Enum(SwipeActionEnum), nullable=False)
    vote_weight = Column(Float, default=1.0)  # Weighted voting support
    priority_score = Column(Integer)  # User's priority ranking (1=highest)
    
    # Timestamps
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GroupSwipeSession", back_populates="votes")
    user = relationship("User")
    content = relationship("TravelContent")
    
    # Constraints
    __table_args__ = (
        Index('idx_session_user_content', 'session_id', 'user_id', 'content_id', unique=True),
    )


class Itinerary(Base):
    """Generated trip itineraries"""
    __tablename__ = 'itineraries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('travel_groups.id'), nullable=True)
    
    # Basic info
    title = Column(String(300), nullable=False)
    description = Column(Text)
    destination = Column(String(200))
    
    # Trip details
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_days = Column(Integer, nullable=False)
    total_budget = Column(Float)
    travelers_count = Column(Integer, default=1)
    
    # Itinerary data
    daily_schedule = Column(JSON)  # Day-by-day schedule
    accommodations = Column(JSON)  # Selected accommodations
    transportation = Column(JSON)  # Transportation bookings
    activities = Column(JSON)  # Planned activities
    
    # Status
    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.DRAFT)
    is_shared = Column(Boolean, default=False)
    share_token = Column(String(100), unique=True)  # For public sharing
    
    # AI metadata
    generated_by_ai = Column(Boolean, default=True)
    ai_confidence = Column(Float)  # AI's confidence in itinerary quality
    personalization_score = Column(Float)  # How well it matches user preferences
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="itineraries")
    group = relationship("TravelGroup", back_populates="itineraries")


class Analytics(Base):
    """Analytics and usage tracking"""
    __tablename__ = 'analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)  # Nullable for anonymous
    
    # Event data
    event_type = Column(String(100), nullable=False, index=True)  # page_view, swipe, booking, etc.
    event_data = Column(JSON)  # Flexible event-specific data
    
    # Context
    session_id = Column(String(100), index=True)
    device_type = Column(String(50))
    browser = Column(String(100))
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    
    # Location (user's location, not travel destination)
    user_country = Column(String(100))
    user_city = Column(String(100))
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_event_type_timestamp', 'event_type', 'timestamp'),
        Index('idx_user_session', 'user_id', 'session_id'),
    )
