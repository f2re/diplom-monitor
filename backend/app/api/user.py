from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.core import security

router = APIRouter()

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
