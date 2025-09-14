"""
Group collaboration API endpoints
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from backend.models.db_config import get_db
from backend.models.database import (
    User, TravelGroup, GroupSwipeSession, GroupSwipeVote, 
    TravelContent, user_group_association
)
from backend.models.schemas import (
    TravelGroupCreate, TravelGroup as TravelGroupSchema,
    GroupDetails, GroupMember, GroupSwipeSessionCreate,
    GroupSwipeSession as GroupSwipeSessionSchema,
    GroupSwipeVoteCreate, SuccessResponse
)
from backend.api.auth import get_current_active_user


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=TravelGroupSchema)
async def create_travel_group(
    group_data: TravelGroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new travel group"""
    
    # Calculate budget per person if total budget provided
    budget_per_person = None
    if group_data.budget_total and group_data.max_members:
        budget_per_person = group_data.budget_total / group_data.max_members
    
    # Create group
    db_group = TravelGroup(
        name=group_data.name,
        description=group_data.description,
        destination=group_data.destination,
        start_date=group_data.start_date,
        end_date=group_data.end_date,
        budget_total=group_data.budget_total,
        budget_per_person=budget_per_person,
        max_members=group_data.max_members,
        is_public=group_data.is_public,
        requires_approval=group_data.requires_approval,
        created_by=current_user.id
    )
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    # Add creator as admin member
    from backend.models.database import GroupRoleEnum
    db.execute(
        user_group_association.insert().values(
            user_id=current_user.id,
            group_id=db_group.id,
            role=GroupRoleEnum.ADMIN
        )
    )
    db.commit()
    
    logger.info(f"Created travel group: {group_data.name} by user {current_user.id}")
    return db_group


@router.get("/", response_model=List[TravelGroupSchema])
async def get_user_groups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's travel groups"""
    
    groups = db.query(TravelGroup).join(
        user_group_association,
        TravelGroup.id == user_group_association.c.group_id
    ).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            TravelGroup.is_active == True
        )
    ).order_by(desc(TravelGroup.created_at)).all()
    
    # Add member count to each group
    group_data = []
    for group in groups:
        member_count = db.query(func.count(user_group_association.c.user_id)).filter(
            user_group_association.c.group_id == group.id
        ).scalar()
        
        group_dict = TravelGroupSchema.from_orm(group).__dict__
        group_dict['member_count'] = member_count
        group_data.append(group_dict)
    
    return group_data


@router.get("/{group_id}", response_model=GroupDetails)
async def get_group_details(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific group"""
    
    # Check if user is member of the group
    membership = db.query(user_group_association).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            user_group_association.c.group_id == group_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
    # Get group details
    group = db.query(TravelGroup).filter(
        and_(
            TravelGroup.id == group_id,
            TravelGroup.is_active == True
        )
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Get all members
    members_query = db.query(
        User, user_group_association.c.role, user_group_association.c.joined_at
    ).join(
        user_group_association, User.id == user_group_association.c.user_id
    ).filter(user_group_association.c.group_id == group_id).all()
    
    members = []
    for user, role, joined_at in members_query:
        members.append(GroupMember(
            user=user,
            role=role,
            joined_at=joined_at
        ))
    
    # Get group creator
    creator = db.query(User).filter(User.id == group.created_by).first()
    
    return GroupDetails(
        **TravelGroupSchema.from_orm(group).__dict__,
        members=members,
        creator=creator,
        member_count=len(members)
    )


@router.post("/{group_id}/join", response_model=SuccessResponse)
async def join_group(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a travel group"""
    
    # Check if group exists and is active
    group = db.query(TravelGroup).filter(
        and_(
            TravelGroup.id == group_id,
            TravelGroup.is_active == True
        )
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if user is already a member
    existing_membership = db.query(user_group_association).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            user_group_association.c.group_id == group_id
        )
    ).first()
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this group"
        )
    
    # Check if group is full
    current_members = db.query(func.count(user_group_association.c.user_id)).filter(
        user_group_association.c.group_id == group_id
    ).scalar()
    
    if current_members >= group.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group is full"
        )
    
    # Add user to group
    from backend.models.database import GroupRoleEnum
    db.execute(
        user_group_association.insert().values(
            user_id=current_user.id,
            group_id=group_id,
            role=GroupRoleEnum.MEMBER
        )
    )
    db.commit()
    
    logger.info(f"User {current_user.id} joined group {group_id}")
    
    return SuccessResponse(
        message="Successfully joined the group",
        data={"group_id": group_id}
    )


@router.post("/{group_id}/leave", response_model=SuccessResponse)
async def leave_group(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Leave a travel group"""
    
    # Check if user is member of the group
    membership = db.query(user_group_association).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            user_group_association.c.group_id == group_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this group"
        )
    
    # Check if user is the group creator
    group = db.query(TravelGroup).filter(TravelGroup.id == group_id).first()
    if group and group.created_by == current_user.id:
        # Transfer ownership to another admin or delete group if no other admins
        other_admins = db.query(user_group_association).filter(
            and_(
                user_group_association.c.group_id == group_id,
                user_group_association.c.user_id != current_user.id,
                user_group_association.c.role == 'admin'
            )
        ).first()
        
        if other_admins:
            # Transfer ownership to first admin
            group.created_by = other_admins.user_id
        else:
            # No other admins, deactivate the group
            group.is_active = False
        
        db.commit()
    
    # Remove user from group
    db.execute(
        user_group_association.delete().where(
            and_(
                user_group_association.c.user_id == current_user.id,
                user_group_association.c.group_id == group_id
            )
        )
    )
    db.commit()
    
    logger.info(f"User {current_user.id} left group {group_id}")
    
    return SuccessResponse(
        message="Successfully left the group",
        data={"group_id": group_id}
    )


@router.post("/{group_id}/swipe-sessions", response_model=GroupSwipeSessionSchema)
async def create_group_swipe_session(
    group_id: str,
    session_data: GroupSwipeSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new group swipe session"""
    
    # Check if user is member of the group
    membership = db.query(user_group_association).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            user_group_association.c.group_id == group_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
    # Create swipe session
    db_session = GroupSwipeSession(
        group_id=group_id,
        session_name=session_data.session_name or f"{session_data.content_type.value} Session",
        content_type=session_data.content_type,
        session_budget_min=session_data.session_budget_min,
        session_budget_max=session_data.session_budget_max,
        max_content_items=session_data.max_content_items
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    logger.info(f"Created group swipe session for group {group_id}")
    return db_session


@router.get("/{group_id}/swipe-sessions", response_model=List[GroupSwipeSessionSchema])
async def get_group_swipe_sessions(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get group's swipe sessions"""
    
    # Check if user is member of the group
    membership = db.query(user_group_association).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            user_group_association.c.group_id == group_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
    sessions = db.query(GroupSwipeSession).filter(
        GroupSwipeSession.group_id == group_id
    ).order_by(desc(GroupSwipeSession.started_at)).all()
    
    return sessions


@router.post("/{group_id}/swipe-sessions/{session_id}/vote", response_model=SuccessResponse)
async def vote_in_group_session(
    group_id: str,
    session_id: str,
    vote_data: GroupSwipeVoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Vote on content in a group swipe session"""
    
    # Check if user is member of the group
    membership = db.query(user_group_association).filter(
        and_(
            user_group_association.c.user_id == current_user.id,
            user_group_association.c.group_id == group_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
    # Check if session exists and is active
    session = db.query(GroupSwipeSession).filter(
        and_(
            GroupSwipeSession.id == session_id,
            GroupSwipeSession.group_id == group_id,
            GroupSwipeSession.is_active == True
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or inactive"
        )
    
    # Find the content
    content = db.query(TravelContent).filter(
        TravelContent.content_id == vote_data.content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check for existing vote and update or create new
    existing_vote = db.query(GroupSwipeVote).filter(
        and_(
            GroupSwipeVote.session_id == session_id,
            GroupSwipeVote.user_id == current_user.id,
            GroupSwipeVote.content_id == content.id
        )
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.action = vote_data.action
        existing_vote.priority_score = vote_data.priority_score
        existing_vote.voted_at = datetime.utcnow()
    else:
        # Create new vote
        vote = GroupSwipeVote(
            session_id=session_id,
            user_id=current_user.id,
            content_id=content.id,
            action=vote_data.action,
            priority_score=vote_data.priority_score
        )
        db.add(vote)
    
    db.commit()
    
    return SuccessResponse(
        message="Vote recorded successfully",
        data={
            "session_id": session_id,
            "content_id": vote_data.content_id,
            "action": vote_data.action.value
        }
    )
