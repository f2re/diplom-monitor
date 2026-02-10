from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.grid import router as grid_router
from app.core.config import settings
from app.core.notifications import start_scheduler
from app.database import engine
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
@app.on_event("startup")
async def startup_event():
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
