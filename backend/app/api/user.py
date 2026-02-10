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
    if user_in.start_date is not None:
        current_user.start_date = user_in.start_date
    if user_in.deadline is not None:
        current_user.deadline = user_in.deadline
    if user_in.emoji is not None:
        current_user.emoji = user_in.emoji
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
