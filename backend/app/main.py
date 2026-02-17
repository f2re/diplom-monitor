from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.grid import router as grid_router
from app.core.config import settings
from app.core.notifications import start_scheduler
from app.database import engine, SessionLocal
from app import models
from app.models import Base

# Создание таблиц при старте (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(grid_router, prefix="/grid", tags=["grid"])

def init_db():
    db = SessionLocal()
    try:
        # Check if any admins exist
        admin_exists = db.query(models.user.User).filter(models.user.User.is_superuser == True).first()
        user_count = db.query(models.user.User).count()

        if not admin_exists and user_count > 0:
            # Promote the first user to admin
            first_user = db.query(models.user.User).order_by(models.user.User.id).first()
            if first_user:
                first_user.is_superuser = True
                db.add(first_user)
                db.commit()
        elif user_count == 1:
            # If there's only one user, they must be admin
            only_user = db.query(models.user.User).first()
            if not only_user.is_superuser:
                only_user.is_superuser = True
                db.add(only_user)
                db.commit()
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    init_db()
    app.state.scheduler = start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    app.state.scheduler.shutdown()

@app.get("/")
async def root():
    return {"message": "Welcome to Weeks Until Diploma API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
