"""
Swipe interaction API endpoints
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from backend.models.db_config import get_db
from backend.models.database import User, SwipeInteraction, TravelContent
from backend.models.schemas import (
    SwipeInteractionCreate, SwipeInteraction as SwipeInteractionSchema,
    SuccessResponse
)
from backend.api.auth import get_current_active_user
from backend.services.gemini_recommendation import GeminiRecommendationEngine


logger = logging.getLogger(__name__)
router = APIRouter()


# Initialize AI engine (will be moved to dependency injection later)
try:
    ai_engine = GeminiRecommendationEngine()
except Exception as e:
    logger.warning(f"AI engine initialization failed: {e}")
    ai_engine = None


def update_user_preferences_async(user_id: str, db: Session):
    """Background task to update user preferences based on recent swipes"""
    try:
        if not ai_engine:
            return
        
        # Get recent swipe interactions
        recent_swipes = db.query(SwipeInteraction).filter(
            SwipeInteraction.user_id == user_id
        ).order_by(desc(SwipeInteraction.timestamp)).limit(100).all()
        
        if len(recent_swipes) < 5:  # Need minimum swipes for analysis
            return
        
        # Convert to AI engine format
        from backend.services.gemini_recommendation import SwipeInteraction as AISwipeInteraction
        from backend.services.gemini_recommendation import SwipeAction, ContentType
        
        ai_swipes = []
        for swipe in recent_swipes:
            ai_swipes.append(AISwipeInteraction(
                user_id=str(swipe.user_id),
                content_id=str(swipe.content_id),
                content_type=ContentType(swipe.content_type.value),
                action=SwipeAction(swipe.action.value),
                timestamp=swipe.timestamp.timestamp(),
                session_id=swipe.session_id
            ))
        
        # Analyze preferences
        preferences = ai_engine.analyze_user_preferences(ai_swipes)
        
        # Update user preferences in database
        from backend.models.database import UserPreference
        user_pref = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if user_pref:
            user_pref.learned_preferences = preferences.get("preferences", {})
            user_pref.preference_confidence = preferences.get("confidence", 0.0)
            user_pref.updated_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"Updated preferences for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        db.rollback()


@router.post("/", response_model=SuccessResponse)
async def create_swipe_interaction(
    swipe_data: SwipeInteractionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a swipe interaction"""
    
    # Find the content by external content_id
    content = db.query(TravelContent).filter(
        TravelContent.content_id == swipe_data.content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check for duplicate swipe in same session
    existing_swipe = db.query(SwipeInteraction).filter(
        and_(
            SwipeInteraction.user_id == current_user.id,
            SwipeInteraction.content_id == content.id,
            SwipeInteraction.session_id == swipe_data.session_id
        )
    ).first()
    
    if existing_swipe:
        # Update existing swipe instead of creating duplicate
        existing_swipe.action = swipe_data.action
        existing_swipe.time_spent_viewing = swipe_data.time_spent_viewing
        existing_swipe.swipe_velocity = swipe_data.swipe_velocity
        existing_swipe.device_type = swipe_data.device_type
        existing_swipe.timestamp = datetime.utcnow()
        
        db.commit()
        
        return SuccessResponse(
            message="Swipe interaction updated",
            data={"swipe_id": str(existing_swipe.id)}
        )
    
    # Get AI prediction for this content (if available)
    prediction_score = None
    explanation = None
    
    if ai_engine:
        try:
            # Get user's swipe history for prediction
            user_swipes = db.query(SwipeInteraction).filter(
                SwipeInteraction.user_id == current_user.id
            ).order_by(desc(SwipeInteraction.timestamp)).limit(50).all()
            
            if user_swipes:
                # Convert to AI format and predict
                from backend.services.gemini_recommendation import (
                    UserProfile, TravelMode, TravelScope, TravelContent as AITravelContent,
                    ContentType
                )
                
                # Create user profile from preferences
                user_pref = current_user.preferences
                if user_pref:
                    ai_user_profile = UserProfile(
                        user_id=str(current_user.id),
                        budget_min=user_pref.default_budget_min or 10000,
                        budget_max=user_pref.default_budget_max or 100000,
                        group_size=user_pref.default_group_size,
                        duration_days=user_pref.default_duration_days,
                        travel_mode=TravelMode(user_pref.default_travel_mode.value),
                        travel_scope=TravelScope(user_pref.default_travel_scope.value)
                    )
                    
                    # Create AI content object
                    ai_content = AITravelContent(
                        content_id=content.content_id,
                        content_type=ContentType(content.content_type.value),
                        title=content.title,
                        description=content.description or "",
                        image_url=content.primary_image_url or "",
                        price_min=content.price_min or 0,
                        price_max=content.price_max or 0,
                        location=content.location,
                        tags=content.tags or [],
                        rating=content.rating or 0,
                        popularity_score=content.popularity_score
                    )
                    
                    # Convert swipe history
                    ai_swipes = []
                    for swipe in user_swipes[:20]:  # Limit for performance
                        ai_swipes.append({
                            "user_id": str(swipe.user_id),
                            "content_id": str(swipe.content_id),
                            "action": swipe.action.value,
                            "timestamp": swipe.timestamp.timestamp(),
                            "session_id": swipe.session_id
                        })
                    
                    # Get prediction and explanation
                    prediction_score = ai_engine.predict_swipe_probability(
                        ai_user_profile, ai_content, []  # Will implement proper conversion later
                    )
                    
                    explanation = ai_engine.explain_recommendation(
                        ai_user_profile, ai_content, []
                    )
        
        except Exception as e:
            logger.warning(f"AI prediction failed: {e}")
    
    # Create swipe interaction record
    swipe_interaction = SwipeInteraction(
        user_id=current_user.id,
        content_id=content.id,
        action=swipe_data.action,
        session_id=swipe_data.session_id,
        content_type=content.content_type,
        time_spent_viewing=swipe_data.time_spent_viewing,
        swipe_velocity=swipe_data.swipe_velocity,
        device_type=swipe_data.device_type,
        prediction_score=prediction_score,
        explanation=explanation
    )
    
    db.add(swipe_interaction)
    db.commit()
    db.refresh(swipe_interaction)
    
    # Schedule background task to update user preferences
    background_tasks.add_task(
        update_user_preferences_async, 
        str(current_user.id), 
        db
    )
    
    logger.info(f"Swipe recorded: user={current_user.id}, content={content.content_id}, action={swipe_data.action}")
    
    return SuccessResponse(
        message="Swipe interaction recorded",
        data={
            "swipe_id": str(swipe_interaction.id),
            "prediction_score": prediction_score,
            "explanation": explanation
        }
    )


@router.get("/history", response_model=List[SwipeInteractionSchema])
async def get_swipe_history(
    session_id: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's swipe history"""
    
    query = db.query(SwipeInteraction).filter(
        SwipeInteraction.user_id == current_user.id
    )
    
    if session_id:
        query = query.filter(SwipeInteraction.session_id == session_id)
    
    if content_type:
        query = query.filter(SwipeInteraction.content_type == content_type)
    
    swipes = query.order_by(desc(SwipeInteraction.timestamp)).offset(offset).limit(limit).all()
    
    return swipes


@router.get("/sessions")
async def get_swipe_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's swipe sessions with statistics"""
    
    # Get session statistics
    from sqlalchemy import func
    
    sessions = db.query(
        SwipeInteraction.session_id,
        func.count(SwipeInteraction.id).label('total_swipes'),
        func.sum(func.case([(SwipeInteraction.action == 'like', 1)], else_=0)).label('likes'),
        func.sum(func.case([(SwipeInteraction.action == 'dislike', 1)], else_=0)).label('dislikes'),
        func.min(SwipeInteraction.timestamp).label('started_at'),
        func.max(SwipeInteraction.timestamp).label('last_activity'),
        SwipeInteraction.content_type
    ).filter(
        SwipeInteraction.user_id == current_user.id
    ).group_by(
        SwipeInteraction.session_id, SwipeInteraction.content_type
    ).order_by(desc('last_activity')).limit(20).all()
    
    session_data = []
    for session in sessions:
        session_data.append({
            "session_id": session.session_id,
            "content_type": session.content_type.value if session.content_type else None,
            "total_swipes": session.total_swipes,
            "likes": session.likes or 0,
            "dislikes": session.dislikes or 0,
            "like_rate": (session.likes or 0) / session.total_swipes if session.total_swipes > 0 else 0,
            "started_at": session.started_at,
            "last_activity": session.last_activity
        })
    
    return {"sessions": session_data}


@router.delete("/session/{session_id}", response_model=SuccessResponse)
async def delete_swipe_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete all swipes from a specific session"""
    
    # Delete swipes for this session
    deleted_count = db.query(SwipeInteraction).filter(
        and_(
            SwipeInteraction.user_id == current_user.id,
            SwipeInteraction.session_id == session_id
        )
    ).delete()
    
    db.commit()
    
    return SuccessResponse(
        message=f"Deleted {deleted_count} swipe interactions from session",
        data={"deleted_count": deleted_count}
    )


@router.get("/analytics")
async def get_swipe_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's swipe analytics and patterns"""
    
    from sqlalchemy import func, extract
    
    # Overall statistics
    total_swipes = db.query(func.count(SwipeInteraction.id)).filter(
        SwipeInteraction.user_id == current_user.id
    ).scalar() or 0
    
    if total_swipes == 0:
        return {
            "total_swipes": 0,
            "like_rate": 0,
            "content_type_breakdown": {},
            "daily_activity": [],
            "preferences_confidence": 0
        }
    
    # Like rate
    likes = db.query(func.count(SwipeInteraction.id)).filter(
        and_(
            SwipeInteraction.user_id == current_user.id,
            SwipeInteraction.action == 'like'
        )
    ).scalar() or 0
    
    like_rate = likes / total_swipes if total_swipes > 0 else 0
    
    # Content type breakdown
    content_breakdown = db.query(
        SwipeInteraction.content_type,
        func.count(SwipeInteraction.id).label('count'),
        func.sum(func.case([(SwipeInteraction.action == 'like', 1)], else_=0)).label('likes')
    ).filter(
        SwipeInteraction.user_id == current_user.id
    ).group_by(SwipeInteraction.content_type).all()
    
    content_stats = {}
    for item in content_breakdown:
        content_stats[item.content_type.value] = {
            "total_swipes": item.count,
            "likes": item.likes or 0,
            "like_rate": (item.likes or 0) / item.count if item.count > 0 else 0
        }
    
    # Daily activity (last 30 days)
    daily_activity = db.query(
        func.date(SwipeInteraction.timestamp).label('date'),
        func.count(SwipeInteraction.id).label('swipes'),
        func.sum(func.case([(SwipeInteraction.action == 'like', 1)], else_=0)).label('likes')
    ).filter(
        and_(
            SwipeInteraction.user_id == current_user.id,
            SwipeInteraction.timestamp >= datetime.utcnow() - timedelta(days=30)
        )
    ).group_by(func.date(SwipeInteraction.timestamp)).order_by('date').all()
    
    activity_data = [
        {
            "date": item.date.isoformat(),
            "swipes": item.swipes,
            "likes": item.likes or 0
        }
        for item in daily_activity
    ]
    
    # Get preferences confidence
    preferences_confidence = 0
    if current_user.preferences:
        preferences_confidence = current_user.preferences.preference_confidence
    
    return {
        "total_swipes": total_swipes,
        "total_likes": likes,
        "like_rate": like_rate,
        "content_type_breakdown": content_stats,
        "daily_activity": activity_data,
        "preferences_confidence": preferences_confidence,
        "analytics_generated_at": datetime.utcnow().isoformat()
    }
