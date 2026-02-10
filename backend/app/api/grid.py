from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app import schemas, models
from app.api import deps

router = APIRouter()

@router.get("/weeks", response_model=List[schemas.week_progress.WeekProgressOut])
def get_weeks(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all week progress for current user.
    """
    return db.query(models.week_progress.WeekProgress).filter(
        models.week_progress.WeekProgress.user_id == current_user.id
    ).all()

@router.get("/weeks/{user_id}", response_model=List[schemas.week_progress.WeekProgressOut])
def get_user_weeks(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all week progress for a specific user.
    """
    return db.query(models.week_progress.WeekProgress).filter(
        models.week_progress.WeekProgress.user_id == user_id
    ).all()

@router.post("/weeks", response_model=schemas.week_progress.WeekProgressOut)
def update_or_create_week(
    *,
    db: Session = Depends(deps.get_db),
    week_in: schemas.week_progress.WeekProgressCreate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update or create week progress. Only current week can be modified.
    """
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    
    if week_in.week_start_date != current_week_start:
        raise HTTPException(
            status_code=403,
            detail="You can only modify the current week."
        )

    week = db.query(models.week_progress.WeekProgress).filter(
        models.week_progress.WeekProgress.user_id == current_user.id,
        models.week_progress.WeekProgress.week_start_date == week_in.week_start_date
    ).first()
    
    if week:
        week.is_completed = week_in.is_completed
        week.note = week_in.note
    else:
        week = models.week_progress.WeekProgress(
            **week_in.model_dump(),
            user_id=current_user.id
        )
    
    db.add(week)
    db.commit()
    db.refresh(week)
    return week

@router.get("/special-periods", response_model=List[schemas.special_period.SpecialPeriodOut])
def get_special_periods(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all special periods for current user.
    """
    return db.query(models.special_period.SpecialPeriod).filter(
        models.special_period.SpecialPeriod.user_id == current_user.id
    ).all()

@router.get("/special-periods/{user_id}", response_model=List[schemas.special_period.SpecialPeriodOut])
def get_user_special_periods(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all special periods for a specific user.
    """
    return db.query(models.special_period.SpecialPeriod).filter(
        models.special_period.SpecialPeriod.user_id == user_id
    ).all()

@router.post("/special-periods", response_model=schemas.special_period.SpecialPeriodOut)
def create_special_period(
    *,
    db: Session = Depends(deps.get_db),
    period_in: schemas.special_period.SpecialPeriodCreate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create special period. Only for self or admin.
    """
    # If user_id is provided in schema, check permissions
    # But SpecialPeriodCreate doesn't have user_id, it's inferred from context or provided?
    # Let's check schemas/special_period.py
    
    period = models.special_period.SpecialPeriod(
        **period_in.model_dump(),
        user_id=current_user.id # Default to self
    )
    db.add(period)
    db.commit()
    db.refresh(period)
    return period

@router.delete("/special-periods/{period_id}")
def delete_special_period(
    *,
    db: Session = Depends(deps.get_db),
    period_id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete special period.
    """
    period = db.query(models.special_period.SpecialPeriod).filter(
        models.special_period.SpecialPeriod.id == period_id
    ).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(period)
    db.commit()
    return {"status": "ok"}

@router.get("/stats/{user_id}", response_model=schemas.week_progress.GridStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get grid statistics for user.
    """
    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.start_date or not user.deadline:
        return {
            "total_weeks": 0,
            "special_weeks": 0,
            "effective_weeks": 0,
            "completed_weeks": 0,
            "remaining_weeks": 0
        }
    
    total_days = (user.deadline - user.start_date).days
    total_weeks = (total_days // 7) + 1
    
    special_periods = db.query(models.special_period.SpecialPeriod).filter(
        models.special_period.SpecialPeriod.user_id == user.id
    ).all()
    
    special_days = 0
    for p in special_periods:
        p_start = max(p.start_date, user.start_date)
        p_end = min(p.end_date, user.deadline)
        if p_start <= p_end:
            special_days += (p_end - p_start).days + 1
            
    special_weeks = special_days // 7
    effective_weeks = max(0, total_weeks - special_weeks)
    
    completed_weeks = db.query(models.week_progress.WeekProgress).filter(
        models.week_progress.WeekProgress.user_id == user.id,
        models.week_progress.WeekProgress.is_completed == True
    ).count()
    
    remaining_weeks = max(0, effective_weeks - completed_weeks)
    
    return {
        "total_weeks": total_weeks,
        "special_weeks": special_weeks,
        "effective_weeks": effective_weeks,
        "completed_weeks": completed_weeks,
        "remaining_weeks": remaining_weeks
    }