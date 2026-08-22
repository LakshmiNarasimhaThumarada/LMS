from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import sys

# Add the parent directory of 'backend' to sys.path so 'backend.*' imports work from anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.config import settings
from backend.routes import planner, notifications, progress, calendar, chat, quiz
from backend.utils.db_indexes import create_indexes

# Database connection
db_client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_client, db
    db_client = AsyncIOMotorClient(settings.MONGO_URI)
    db = db_client[settings.DATABASE_NAME]
    app.state.db = db
    
    # Create database indexes
    await create_indexes(db)
    
    yield
    
    # Shutdown
    db_client.close()

app = FastAPI(
    title="EduMind Study Planner API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(planner.router, prefix="/api/planner", tags=["Study Planner"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat Agent"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz Agent"])

@app.get("/")
async def root():
    return {"message": "EduMind Study Planner API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
