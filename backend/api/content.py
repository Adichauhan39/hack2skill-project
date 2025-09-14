"""
Travel content management API endpoints
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from backend.models.db_config import get_db
from backend.models.database import TravelContent
from backend.models.schemas import (
    TravelContent as TravelContentSchema,
    TravelContentCreate,
    ContentType,
    SuccessResponse
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[TravelContentSchema])
async def get_travel_content(
    content_type: Optional[ContentType] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get travel content with filters"""
    
    query = db.query(TravelContent).filter(TravelContent.is_active == True)
    
    # Apply filters
    if content_type:
        query = query.filter(TravelContent.content_type == content_type)
    
    if location:
        query = query.filter(
            or_(
                TravelContent.location.ilike(f"%{location}%"),
                TravelContent.city.ilike(f"%{location}%"),
                TravelContent.state.ilike(f"%{location}%"),
                TravelContent.country.ilike(f"%{location}%")
            )
        )
    
    if min_price is not None:
        query = query.filter(TravelContent.price_min >= min_price)
    
    if max_price is not None:
        query = query.filter(TravelContent.price_max <= max_price)
    
    if min_rating is not None:
        query = query.filter(TravelContent.rating >= min_rating)
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        # PostgreSQL JSON contains operator
        for tag in tag_list:
            query = query.filter(func.json_extract_path_text(TravelContent.tags, tag).isnot(None))
    
    # Order by popularity and rating
    content = query.order_by(
        desc(TravelContent.popularity_score),
        desc(TravelContent.rating)
    ).offset(offset).limit(limit).all()
    
    return content


@router.get("/{content_id}", response_model=TravelContentSchema)
async def get_content_by_id(
    content_id: str,
    db: Session = Depends(get_db)
):
    """Get specific travel content by ID"""
    
    content = db.query(TravelContent).filter(
        and_(
            TravelContent.content_id == content_id,
            TravelContent.is_active == True
        )
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return content


@router.get("/search/text")
async def search_content(
    q: str = Query(..., min_length=2, description="Search query"),
    content_type: Optional[ContentType] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search travel content by text"""
    
    query = db.query(TravelContent).filter(TravelContent.is_active == True)
    
    # Text search across title, description, and location
    search_filter = or_(
        TravelContent.title.ilike(f"%{q}%"),
        TravelContent.description.ilike(f"%{q}%"),
        TravelContent.short_description.ilike(f"%{q}%"),
        TravelContent.location.ilike(f"%{q}%"),
        TravelContent.city.ilike(f"%{q}%"),
        TravelContent.state.ilike(f"%{q}%")
    )
    
    query = query.filter(search_filter)
    
    if content_type:
        query = query.filter(TravelContent.content_type == content_type)
    
    # Order by relevance (popularity and rating)
    results = query.order_by(
        desc(TravelContent.popularity_score),
        desc(TravelContent.rating)
    ).offset(offset).limit(limit).all()
    
    return {
        "query": q,
        "results": [TravelContentSchema.from_orm(item) for item in results],
        "total_results": len(results),
        "limit": limit,
        "offset": offset
    }


@router.get("/locations/popular")
async def get_popular_locations(
    content_type: Optional[ContentType] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get popular travel locations"""
    
    query = db.query(
        TravelContent.city,
        TravelContent.state,
        TravelContent.country,
        func.count(TravelContent.id).label('content_count'),
        func.avg(TravelContent.rating).label('avg_rating'),
        func.avg(TravelContent.popularity_score).label('avg_popularity')
    ).filter(TravelContent.is_active == True)
    
    if content_type:
        query = query.filter(TravelContent.content_type == content_type)
    
    locations = query.group_by(
        TravelContent.city,
        TravelContent.state,
        TravelContent.country
    ).having(
        func.count(TravelContent.id) > 1  # At least 2 content items
    ).order_by(
        desc('avg_popularity'),
        desc('content_count')
    ).limit(limit).all()
    
    location_data = []
    for loc in locations:
        location_data.append({
            "city": loc.city,
            "state": loc.state,
            "country": loc.country,
            "content_count": loc.content_count,
            "average_rating": round(loc.avg_rating or 0, 2),
            "popularity_score": round(loc.avg_popularity or 0, 2)
        })
    
    return {"popular_locations": location_data}


@router.post("/", response_model=TravelContentSchema)
async def create_travel_content(
    content_data: TravelContentCreate,
    db: Session = Depends(get_db)
):
    """Create new travel content (admin/system use)"""
    
    # Check if content with same content_id already exists
    existing = db.query(TravelContent).filter(
        TravelContent.content_id == content_data.content_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content with this ID already exists"
        )
    
    # Create new content
    db_content = TravelContent(
        content_id=content_data.content_id,
        content_type=content_data.content_type,
        title=content_data.title,
        description=content_data.description,
        short_description=content_data.short_description,
        location=content_data.location,
        city=content_data.city,
        state=content_data.state,
        country=content_data.country,
        latitude=content_data.latitude,
        longitude=content_data.longitude,
        price_min=content_data.price_min,
        price_max=content_data.price_max,
        currency=content_data.currency,
        rating=content_data.rating,
        primary_image_url=content_data.primary_image_url,
        image_urls=content_data.image_urls,
        tags=content_data.tags,
        features=content_data.features,
        created_by="api"
    )
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    logger.info(f"Created new travel content: {content_data.content_id}")
    return db_content


@router.get("/stats/overview")
async def get_content_stats(db: Session = Depends(get_db)):
    """Get travel content statistics"""
    
    # Overall stats
    total_content = db.query(func.count(TravelContent.id)).filter(
        TravelContent.is_active == True
    ).scalar()
    
    # Stats by content type
    type_stats = db.query(
        TravelContent.content_type,
        func.count(TravelContent.id).label('count'),
        func.avg(TravelContent.rating).label('avg_rating'),
        func.avg(TravelContent.popularity_score).label('avg_popularity')
    ).filter(TravelContent.is_active == True).group_by(
        TravelContent.content_type
    ).all()
    
    type_breakdown = {}
    for stat in type_stats:
        type_breakdown[stat.content_type.value] = {
            "count": stat.count,
            "average_rating": round(stat.avg_rating or 0, 2),
            "average_popularity": round(stat.avg_popularity or 0, 2)
        }
    
    # Price ranges by type
    price_ranges = db.query(
        TravelContent.content_type,
        func.min(TravelContent.price_min).label('min_price'),
        func.max(TravelContent.price_max).label('max_price'),
        func.avg(TravelContent.price_min).label('avg_min_price'),
        func.avg(TravelContent.price_max).label('avg_max_price')
    ).filter(
        and_(
            TravelContent.is_active == True,
            TravelContent.price_min.isnot(None),
            TravelContent.price_max.isnot(None)
        )
    ).group_by(TravelContent.content_type).all()
    
    price_data = {}
    for price in price_ranges:
        price_data[price.content_type.value] = {
            "min_price": price.min_price,
            "max_price": price.max_price,
            "avg_min_price": round(price.avg_min_price or 0, 2),
            "avg_max_price": round(price.avg_max_price or 0, 2)
        }
    
    return {
        "total_content": total_content,
        "content_by_type": type_breakdown,
        "price_ranges": price_data,
        "generated_at": datetime.utcnow().isoformat()
    }
