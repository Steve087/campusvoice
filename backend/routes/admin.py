from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import json
from services.auth import require_admin, hash_password, validate_email_domain
from models.schemas import RegisterRequest, UserOut, FeedbackItem
from services.embeddings import generate_embeddings
from services.clustering import cluster_feedback
from services.sentiment import analyze_sentiment
from models.db_models import User, Session as DBSession, AnalysisResult, FeedbackItem as DBFeedbackItem

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    return db.query(User).all()


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} deactivated"}


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {user.email} activated"}


@router.get("/sessions")
def list_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    sessions = db.query(DBSession).order_by(DBSession.created_at.desc()).all()
    return [
        {
            "session_id": s.session_id,
            "total_rows": s.total_rows,
            "created_at": s.created_at,
            "has_analysis": s.analysis_result is not None
        }
        for s in sessions
    ]


@router.get("/results/{session_id}")
def get_result(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = db.query(AnalysisResult).filter(
        AnalysisResult.session_id == session_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="No analysis found for this session")

    return {
        "session_id": result.session_id,
        "clusters": json.loads(result.clusters_json),
        "department_sentiments": json.loads(result.department_sentiments_json),
        "urgent_items": json.loads(result.urgent_items_json),
        "noise_count": result.noise_count,
        "created_at": result.created_at
    }

# routes/admin.py — add this

@router.post("/create-admin")
def create_admin(
    req: RegisterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    if not validate_email_domain(req.email):
        raise HTTPException(status_code=400, detail="Only @cec.ac.in emails allowed")

    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        role="admin"
    )
    db.add(user)
    db.commit()
    return {"message": f"Admin {user.email} created"}

@router.get("/submissions/analyze")
def analyze_submissions(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    items = db.query(DBFeedbackItem).filter(
        DBFeedbackItem.session_id.like("direct-%")
    ).all()

    if len(items) < 2:  # ← need at least 2 items
        return {
            "total_feedback": len(items),
            "total_clusters": 0,
            "clusters": [],
            "noise_count": len(items),
            "urgent_items": [],
            "department_sentiments": {}
        }

    feedback = [
        FeedbackItem(
            id=item.item_id,
            text=item.text,
            department=item.department,
            subject=item.subject
        )
        for item in items
    ]

    texts = [item.text for item in feedback]
    vectors = generate_embeddings(texts)
    clusters, noise = cluster_feedback(feedback, vectors, min_cluster_size=2)
    clusters, urgent_items, dept_sentiments = analyze_sentiment(clusters, noise)

    return {
        "total_feedback": len(feedback),
        "total_clusters": len(clusters),
        "clusters": [c.model_dump() for c in clusters],
        "noise_count": len(noise),
        "urgent_items": [i.model_dump() for i in urgent_items],
        "department_sentiments": dept_sentiments
    }