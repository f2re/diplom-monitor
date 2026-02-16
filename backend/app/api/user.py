from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.core import security

router = APIRouter()

@router.get("/", response_model=List[schemas.user.UserPublic])
def get_users(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get all active users.
    """
    return db.query(models.user.User).filter(models.user.User.is_active == True).all()

@router.get("/me", response_model=schemas.user.UserOut)
def get_user_me(
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get own user.
    """
    return current_user

@router.get("/{user_id}", response_model=schemas.user.UserPublicProfile)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get public profile of a user.
    """
    user = db.query(models.user.User).filter(models.user.User.id == user_id, models.user.User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=schemas.user.UserOut)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserUpdate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.password is not None:
        current_user.hashed_password = security.get_password_hash(user_in.password)
    
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    
    # Only superusers can update start_date and deadline
    if user_in.start_date is not None and user_in.start_date != current_user.start_date:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only admins can change the start date")
        current_user.start_date = user_in.start_date
        
    if user_in.deadline is not None and user_in.deadline != current_user.deadline:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only admins can change the deadline")
        current_user.deadline = user_in.deadline
        
    if user_in.emoji is not None and user_in.emoji != current_user.emoji:
        # Check if emoji is already taken
        existing_user = db.query(models.user.User).filter(
            models.user.User.emoji == user_in.emoji,
            models.user.User.id != current_user.id,
            models.user.User.is_active == True
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Этот эмодзи уже занят другим участником")
        current_user.emoji = user_in.emoji
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
