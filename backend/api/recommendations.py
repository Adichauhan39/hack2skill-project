"""
AI Recommendations API endpoints
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, not_, desc, func

from backend.models.db_config import get_db
from backend.models.database import User, TravelContent, SwipeInteraction, UserPreference, ContentTypeEnum
from backend.models.schemas import (
    RecommendationRequest, RecommendationResponse, RecommendationItem,
    TravelContent as TravelContentSchema, ContentType
)


def map_content_type_to_db_enum(api_content_type: ContentType) -> ContentTypeEnum:
    """Map API ContentType enum to database ContentTypeEnum"""
    mapping = {
        ContentType.DESTINATION: ContentTypeEnum.DESTINATION,
        ContentType.ACCOMMODATION: ContentTypeEnum.ACCOMMODATION,
        ContentType.ACTIVITY: ContentTypeEnum.ACTIVITY,
        ContentType.TRANSPORTATION: ContentTypeEnum.TRANSPORTATION
    }
    return mapping[api_content_type]
from backend.api.auth import get_current_active_user
from backend.services.gemini_recommendation import GeminiRecommendationEngine


logger = logging.getLogger(__name__)
router = APIRouter()


# Initialize Gemini AI engine
try:
    ai_engine = GeminiRecommendationEngine()
except Exception as e:
    logger.warning(f"Gemini AI engine initialization failed: {e}")
    ai_engine = None


def get_user_budget_context(user: User, request: RecommendationRequest) -> tuple:
    """Get user's budget context from preferences or request"""
    budget_min = request.budget_min
    budget_max = request.budget_max
    
    # Use user preferences as fallback
    if user.preferences and (budget_min is None or budget_max is None):
        if budget_min is None:
            budget_min = user.preferences.default_budget_min or 10000
        if budget_max is None:
            budget_max = user.preferences.default_budget_max or 100000
    
    # Final fallbacks
    budget_min = budget_min or 10000
    budget_max = budget_max or 100000
    
    return budget_min, budget_max


def convert_db_content_to_ai_format(content_items: List[TravelContent]) -> List:
    """Convert database content to AI engine format"""
    from backend.services.gemini_recommendation import (
        TravelContent as AITravelContent, ContentType as AIContentType
    )
    
    ai_content = []
    for content in content_items:
        try:
            ai_content.append(AITravelContent(
                content_id=content.content_id,
                content_type=AIContentType(content.content_type.value),
                title=content.title,
                description=content.description or "",
                image_url=content.primary_image_url or "",
                price_min=content.price_min or 0,
                price_max=content.price_max or 0,
                location=content.location,
                tags=content.tags or [],
                rating=content.rating or 0,
                popularity_score=content.popularity_score
            ))
        except Exception as e:
            logger.warning(f"Failed to convert content {content.content_id}: {e}")
            continue
    
    return ai_content


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for user"""
    
    # Generate session ID if not provided
    session_id = request.session_id or f"rec_{uuid.uuid4().hex[:12]}"
    
    # Get user's budget context
    budget_min, budget_max = get_user_budget_context(current_user, request)
    
    # Get content that user hasn't swiped on yet
    swiped_content_ids = db.query(SwipeInteraction.content_id).filter(
        SwipeInteraction.user_id == current_user.id
    ).subquery()
    
    # Convert API content type to database enum
    db_content_type = map_content_type_to_db_enum(request.content_type)
    
    # Base query for available content
    content_query = db.query(TravelContent).filter(
        and_(
            TravelContent.content_type == db_content_type,
            TravelContent.is_active == True,
            not_(TravelContent.id.in_(swiped_content_ids))
        )
    )
    
    # Apply budget filter
    if budget_min is not None and budget_max is not None:
        content_query = content_query.filter(
            and_(
                TravelContent.price_min <= budget_max,
                TravelContent.price_max >= budget_min
            )
        )
    
    # Exclude specific content IDs if requested
    if request.exclude_content_ids:
        content_query = content_query.filter(
            not_(TravelContent.content_id.in_(request.exclude_content_ids))
        )
    
    # Get available content
    available_content = content_query.order_by(
        desc(TravelContent.popularity_score),
        desc(TravelContent.rating)
    ).limit(200).all()  # Get more than needed for AI to choose from
    
    total_available = len(available_content)
    
    if not available_content:
        return RecommendationResponse(
            items=[],
            total_available=0,
            user_preferences_confidence=0.0,
            session_id=session_id,
            generated_at=datetime.utcnow()
        )
    
    # Use AI for recommendations if available
    recommendations = []
    preferences_confidence = 0.0
    
    if ai_engine:
        try:
            # Get user's swipe history
            user_swipes = db.query(SwipeInteraction).filter(
                SwipeInteraction.user_id == current_user.id
            ).order_by(desc(SwipeInteraction.timestamp)).limit(100).all()
            
            # Convert to AI format
            from backend.services.gemini_recommendation import (
                UserProfile, TravelMode, TravelScope, SwipeInteraction as AISwipeInteraction,
                SwipeAction, ContentType as AIContentType, RecommendationRequest as AIRecommendationRequest
            )
            
            # Create user profile
            user_profile = UserProfile(
                user_id=str(current_user.id),
                budget_min=budget_min,
                budget_max=budget_max,
                group_size=request.group_size or (current_user.preferences.default_group_size if current_user.preferences else 1),
                duration_days=request.duration_days or (current_user.preferences.default_duration_days if current_user.preferences else 7),
                travel_mode=TravelMode(request.travel_mode.value if request.travel_mode else 
                                     (current_user.preferences.default_travel_mode.value if current_user.preferences else "pleasure")),
                travel_scope=TravelScope((current_user.preferences.default_travel_scope.value if current_user.preferences else "india"))
            )
            
            # Convert swipe history
            ai_swipes = []
            for swipe in user_swipes:
                ai_swipes.append(AISwipeInteraction(
                    user_id=str(swipe.user_id),
                    content_id=str(swipe.content_id),
                    content_type=AIContentType(swipe.content_type.value),
                    action=SwipeAction(swipe.action.value),
                    timestamp=swipe.timestamp.timestamp(),
                    session_id=swipe.session_id
                ))
            
            # Create AI recommendation request
            ai_request = AIRecommendationRequest(
                user_profile=user_profile,
                previous_swipes=ai_swipes,
                content_type=AIContentType(request.content_type.value),
                batch_size=request.batch_size,
                exclude_content_ids=request.exclude_content_ids or []
            )
            
            # Convert content to AI format
            ai_content = convert_db_content_to_ai_format(available_content)
            
            # Get AI recommendations
            ai_recommendations = await ai_engine.generate_recommendations(ai_request, ai_content)
            
            # Convert back to response format
            content_map = {c.content_id: c for c in available_content}
            
            for ai_content_item, score in ai_recommendations:
                if ai_content_item.content_id in content_map:
                    db_content = content_map[ai_content_item.content_id]
                    
                    # Get explanation
                    explanation = None
                    try:
                        explanation = ai_engine.explain_recommendation(
                            user_profile, ai_content_item, ai_swipes
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get explanation: {e}")
                    
                    # Get prediction probability
                    prediction_prob = None
                    try:
                        prediction_prob = ai_engine.predict_swipe_probability(
                            user_profile, ai_content_item, ai_swipes
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get prediction: {e}")
                    
                    recommendations.append(RecommendationItem(
                        content=TravelContentSchema.from_orm(db_content),
                        relevance_score=score,
                        explanation=explanation,
                        prediction_probability=prediction_prob
                    ))
            
            # Get preferences confidence
            if current_user.preferences:
                preferences_confidence = current_user.preferences.preference_confidence
            
        except Exception as e:
            logger.error(f"AI recommendation failed: {e}")
            # Fallback to simple recommendations
            
    # Fallback to simple recommendations if AI failed or not available
    if not recommendations:
        # Simple scoring based on rating and popularity
        for content in available_content[:request.batch_size]:
            score = 0.0
            
            # Rating score (0-0.5)
            if content.rating:
                score += (content.rating / 5.0) * 0.5
            
            # Popularity score (0-0.3)
            score += (content.popularity_score / 100.0) * 0.3
            
            # Budget fit score (0-0.2)
            if content.price_min and content.price_max and budget_min and budget_max:
                if content.price_min <= budget_max and content.price_max >= budget_min:
                    score += 0.2
            
            recommendations.append(RecommendationItem(
                content=TravelContentSchema.from_orm(content),
                relevance_score=min(score, 1.0),
                explanation="Recommended based on popularity and rating"
            ))
    
    logger.info(f"Generated {len(recommendations)} recommendations for user {current_user.id}")
    
    return RecommendationResponse(
        items=recommendations,
        total_available=total_available,
        user_preferences_confidence=preferences_confidence,
        session_id=session_id,
        generated_at=datetime.utcnow()
    )


@router.get("/popular/{content_type}")
async def get_popular_content(
    content_type: ContentType,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get popular content by type (no authentication required)"""
    
    # Convert API content type to database enum
    db_content_type = map_content_type_to_db_enum(content_type)
    
    content = db.query(TravelContent).filter(
        and_(
            TravelContent.content_type == db_content_type,
            TravelContent.is_active == True
        )
    ).order_by(
        desc(TravelContent.popularity_score),
        desc(TravelContent.rating)
    ).offset(offset).limit(limit).all()
    
    return {
        "content": [TravelContentSchema.from_orm(item) for item in content],
        "content_type": content_type,
        "limit": limit,
        "offset": offset
    }


@router.get("/trending")
async def get_trending_content(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending content based on recent swipe activity"""
    
    # Get content with most likes in recent days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    trending = db.query(
        TravelContent,
        func.count(SwipeInteraction.id).label('recent_likes')
    ).join(
        SwipeInteraction, TravelContent.id == SwipeInteraction.content_id
    ).filter(
        and_(
            SwipeInteraction.action == 'like',
            SwipeInteraction.timestamp >= cutoff_date,
            TravelContent.is_active == True
        )
    ).group_by(TravelContent.id).order_by(
        desc('recent_likes'),
        desc(TravelContent.popularity_score)
    ).limit(limit).all()
    
    trending_content = []
    for content, like_count in trending:
        content_data = TravelContentSchema.from_orm(content)
        trending_content.append({
            "content": content_data,
            "recent_likes": like_count,
            "trending_score": like_count  # Could be more sophisticated
        })
    
    return {
        "trending_content": trending_content,
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.post("/explain")
async def explain_recommendation(
    content_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get explanation for why specific content was recommended"""
    
    if not ai_engine:
        return {
            "explanation": "This content matches your general preferences and budget.",
            "confidence": 0.5
        }
    
    # Find the content
    content = db.query(TravelContent).filter(
        TravelContent.content_id == content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    try:
        # Get user's swipe history
        user_swipes = db.query(SwipeInteraction).filter(
            SwipeInteraction.user_id == current_user.id
        ).order_by(desc(SwipeInteraction.timestamp)).limit(50).all()
        
        # Convert to AI format
        from backend.services.gemini_recommendation import (
            UserProfile, TravelMode, TravelScope, TravelContent as AITravelContent,
            ContentType as AIContentType
        )
        
        # Create user profile
        user_profile = UserProfile(
            user_id=str(current_user.id),
            budget_min=current_user.preferences.default_budget_min if current_user.preferences else 10000,
            budget_max=current_user.preferences.default_budget_max if current_user.preferences else 100000,
            group_size=current_user.preferences.default_group_size if current_user.preferences else 1,
            duration_days=current_user.preferences.default_duration_days if current_user.preferences else 7,
            travel_mode=TravelMode(current_user.preferences.default_travel_mode.value if current_user.preferences else "pleasure"),
            travel_scope=TravelScope(current_user.preferences.default_travel_scope.value if current_user.preferences else "india")
        )
        
        # Convert content to AI format
        ai_content = AITravelContent(
            content_id=content.content_id,
            content_type=AIContentType(content.content_type.value),
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
        
        # Get explanation
        explanation = ai_engine.explain_recommendation(user_profile, ai_content, [])
        
        # Get prediction probability
        prediction_prob = ai_engine.predict_swipe_probability(user_profile, ai_content, [])
        
        return {
            "explanation": explanation,
            "prediction_probability": prediction_prob,
            "content_title": content.title,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}")
        return {
            "explanation": "This content matches your preferences and budget.",
            "confidence": 0.5,
            "error": "AI explanation temporarily unavailable"
        }
