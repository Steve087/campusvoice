# backend/models/schemas.py

from pydantic import BaseModel
from typing import Optional


# --- FEEDBACK ITEM ---
# One row of feedback after parsing the CSV
class FeedbackItem(BaseModel):
    id: int
    text: str
    department: Optional[str] = None  # None if column missing in CSV
    subject: Optional[str] = None


# --- UPLOAD ---
# What /upload returns to the frontend after parsing CSV
class UploadResponse(BaseModel):
    session_id: str           # UUID — frontend uses this for all future requests
    total_rows: int           # how many feedback rows were found
    preview: list[str]        # first 5 texts so user can verify it parsed correctly
    departments: list[str]    # unique departments found in the CSV


# --- EMBED ---
# What frontend sends to /embed
class EmbedRequest(BaseModel):
    session_id: str

# What /embed returns after generating vectors
class EmbedResponse(BaseModel):
    session_id: str
    vectors_shape: list[int]  # [120, 384] — 120 feedbacks, 384 dimensions
    status: str               # "embedded"


# --- ANALYZE ---
# What frontend sends to /analyze
class AnalyzeRequest(BaseModel):
    session_id: str
    min_cluster_size: int = 3  # default 3, frontend can override

# One cluster of similar feedback
class FeedbackCluster(BaseModel):
    cluster_id: int
    label: str              # most representative sentence from the cluster
    size: int               # number of feedbacks in this cluster
    items: list[FeedbackItem]
    sentiment_score: float  # average sentiment, -1.0 to +1.0
    is_urgent: bool         # True if sentiment_score < -0.5

# The full analysis result
class AnalysisResult(BaseModel):
    session_id: str
    total_feedback: int
    total_clusters: int
    clusters: list[FeedbackCluster]
    noise_count: int                    # feedbacks that didn't fit any cluster
    urgent_items: list[FeedbackItem]    # strongly negative individual feedbacks
    department_sentiments: dict[str, float]  # { "CSE": -0.3, "ECE": 0.6 }