# routes/analyze.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import FeedbackItem as DBFeedbackItem, AnalysisResult as DBAnalysisResult
from models.schemas import AnalyzeRequest, AnalysisResult, FeedbackItem
from services.clustering import cluster_feedback
from services.sentiment import analyze_sentiment
from services.embeddings import generate_embeddings
from services.auth import require_admin
import state
import json

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/", response_model=AnalysisResult)
def analyze_feedback(
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    # 1. Load feedback from DB
    db_items = db.query(DBFeedbackItem).filter(
        DBFeedbackItem.session_id == req.session_id
    ).all()

    if not db_items:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Convert to schema objects
    feedback = [
        FeedbackItem(
            id=item.item_id,
            text=item.text,
            department=item.department,
            subject=item.subject
        )
        for item in db_items
    ]

    # 3. Generate embeddings inline
    texts = [item.text for item in feedback]
    vectors = generate_embeddings(texts)

    # 4. Cluster
    clusters, noise = cluster_feedback(feedback, vectors, req.min_cluster_size)

    # 5. Sentiment
    clusters, urgent_items, dept_sentiments = analyze_sentiment(clusters, noise)

    # 6. Save to DB
    existing = db.query(DBAnalysisResult).filter(
        DBAnalysisResult.session_id == req.session_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    db_result = DBAnalysisResult(
        session_id=req.session_id,
        clusters_json=json.dumps([c.model_dump() for c in clusters]),
        department_sentiments_json=json.dumps(dept_sentiments),
        urgent_items_json=json.dumps([i.model_dump() for i in urgent_items]),
        noise_count=len(noise)
    )
    db.add(db_result)
    db.commit()

    return AnalysisResult(
    session_id=req.session_id,
    total_feedback=len(feedback),
    total_clusters=len(clusters),
    clusters=clusters,
    noise_count=len(noise),
    noise_items=noise,              # ← add this
    urgent_items=urgent_items,
    department_sentiments=dept_sentiments
)