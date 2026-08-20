from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

class Chapter(BaseModel):
    number: Union[int, float, str]
    name: str
    topics: List[str]

class EstimatedHours(BaseModel):
    study: float
    practice: float
    review: float
    total: float
    per_chapter: float

class PDFAnalysisResult(BaseModel):
    chapters: List[Chapter]
    total_topics: int
    estimated_hours: EstimatedHours
    difficulty: str
    page_count: int

class PDFAnalysisResponse(BaseModel):
    pdf_id: str
    filename: str
    analysis: PDFAnalysisResult
    created_at: datetime

class StudyPreferences(BaseModel):
    exam_date: str = Field(..., description="YYYY-MM-DD format")
    hours_per_day: float = Field(ge=0.5, le=8.0, description="Study hours per day")
    preferred_times: List[str] = Field(default=['morning'], description="morning, afternoon, evening, night")
    study_style: str = Field(default='distributed', description="distributed or intensive")
    skip_weekends: bool = Field(default=True)

class Session(BaseModel):
    id: str
    date: str
    time: str
    chapter_number: Optional[Union[int, float, str]] = None
    chapter_name: str
    topics: List[str] = Field(default=[])
    duration: float
    type: str  # study, review_1, review_7, practice
    completed: bool = False
    difficulty_rating: Optional[str] = None  # easy, medium, hard
    actual_time: Optional[float] = None
    completed_at: Optional[datetime] = None

class ScheduleSummary(BaseModel):
    total_sessions: int
    study_sessions: int
    review_sessions: int
    practice_sessions: int
    total_hours: float
    chapters_covered: int
    start_date: str
    end_date: str
    exam_date: str

class StudyPlan(BaseModel):
    plan_id: str
    user_id: str
    pdf_id: str
    pdf_filename: str
    sessions: List[Session]
    summary: ScheduleSummary
    preferences: StudyPreferences
    created_at: datetime
    status: str = 'active'  # active, paused, completed

class GeneratePlanRequest(BaseModel):
    pdf_id: str
    preferences: StudyPreferences

class GeneratePlanResponse(BaseModel):
    plan_id: str
    sessions: List[Session]
    summary: ScheduleSummary
    created_at: datetime
