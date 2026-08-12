from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- AUTH ---
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- FEEDBACK ---
class FeedbackSubmit(BaseModel):
    text: str
    department: Optional[str] = None
    subject: Optional[str] = None

class FeedbackItem(BaseModel):
    id: int
    text: str
    department: Optional[str] = None
    subject: Optional[str] = None


# --- UPLOAD ---
class UploadResponse(BaseModel):
    session_id: str
    total_rows: int
    preview: list[str]
    departments: list[str]


# --- EMBED ---
class EmbedRequest(BaseModel):
    session_id: str

class EmbedResponse(BaseModel):
    session_id: str
    vectors_shape: list[int]
    status: str


# --- ANALYZE ---
class AnalyzeRequest(BaseModel):
    session_id: str
    min_cluster_size: int = 3

class FeedbackCluster(BaseModel):
    cluster_id: int
    label: str
    size: int
    items: list[FeedbackItem]
    sentiment_score: float
    is_urgent: bool

class AnalysisResult(BaseModel):
    session_id: str
    total_feedback: int
    total_clusters: int
    clusters: list[FeedbackCluster]
    noise_count: int
    noise_items: list[FeedbackItem]      # ← add this
    urgent_items: list[FeedbackItem]
    department_sentiments: dict[str, float]