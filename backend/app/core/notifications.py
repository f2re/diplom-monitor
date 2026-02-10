import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from telegram import Bot
from app.core.config import settings
from app.models.user import User
from app.models.week_progress import WeekProgress
from app.database import SessionLocal

async def send_reminders():
    if settings.TELEGRAM_BOT_TOKEN == 'SET_YOUR_BOT_TOKEN':
        print('Telegram Bot Token not set, skipping reminders')
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    db = SessionLocal()
    try:
        # Calculate current week start date (Monday)
        today = datetime.now().date()
        current_week_start = today - timedelta(days=today.weekday())
        
        # Get users with telegram_id
        users = db.query(User).filter(User.telegram_id.isnot(None)).all()
        
        for user in users:
            # Check if progress exists for current week
            progress = db.query(WeekProgress).filter(
                WeekProgress.user_id == user.id,
                WeekProgress.week_start_date == current_week_start
            ).first()
            
            if not progress or not progress.is_completed:
                message = '👋 Привет! Не забудь отметить прогресс за эту неделю в Weeks Until Diploma!'
                try:
                    await bot.send_message(chat_id=user.telegram_id, text=message)
                except Exception as e:
                    print(f'Failed to send message to {user.telegram_id}: {e}')
    finally:
        db.close()

def start_scheduler():
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    # Every Sunday at 18:00
    scheduler.add_job(send_reminders, 'cron', day_of_week='sun', hour=18)
    scheduler.start()
    return scheduler
