"""
User management API endpoints
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.models.db_config import get_db
from backend.models.database import User, UserPreference
from backend.models.schemas import (
    UserProfile, UserUpdate, UserPreferences, UserPreferencesCreate,
    SuccessResponse
)
from backend.api.auth import get_current_active_user


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user's information"""
    return current_user


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update user fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.phone_number is not None:
        current_user.phone_number = profile_data.phone_number
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.location is not None:
        current_user.location = profile_data.location
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"User profile updated: {current_user.email}")
    return current_user


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's preferences"""
    
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Create default preferences
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences_data: UserPreferencesCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's preferences"""
    
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
    
    # Update preferences
    if preferences_data.default_budget_min is not None:
        preferences.default_budget_min = preferences_data.default_budget_min
    if preferences_data.default_budget_max is not None:
        preferences.default_budget_max = preferences_data.default_budget_max
    if preferences_data.default_group_size is not None:
        preferences.default_group_size = preferences_data.default_group_size
    if preferences_data.default_duration_days is not None:
        preferences.default_duration_days = preferences_data.default_duration_days
    if preferences_data.default_travel_mode is not None:
        preferences.default_travel_mode = preferences_data.default_travel_mode
    if preferences_data.default_travel_scope is not None:
        preferences.default_travel_scope = preferences_data.default_travel_scope
    
    if preferences_data.dietary_preferences is not None:
        preferences.dietary_preferences = preferences_data.dietary_preferences
    if preferences_data.accessibility_needs is not None:
        preferences.accessibility_needs = preferences_data.accessibility_needs
    if preferences_data.transport_preferences is not None:
        preferences.transport_preferences = preferences_data.transport_preferences
    if preferences_data.accommodation_preferences is not None:
        preferences.accommodation_preferences = preferences_data.accommodation_preferences
    
    db.commit()
    db.refresh(preferences)
    
    logger.info(f"User preferences updated: {current_user.email}")
    return preferences


@router.delete("/account", response_model=SuccessResponse)
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account (soft delete)"""
    
    # Soft delete - just deactivate the account
    current_user.is_active = False
    db.commit()
    
    logger.info(f"User account deactivated: {current_user.email}")
    
    return SuccessResponse(
        message="Account successfully deactivated",
        data={"user_id": str(current_user.id)}
    )
