from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import FeedbackItem as DBFeedbackItem, Session as DBSession
from models.schemas import FeedbackSubmit, FeedbackItem
from services.auth import get_current_user
import state
import uuid

router = APIRouter(prefix="/feedback", tags=["feedback"])


def is_appropriate(text: str) -> bool:
    # Rule-based checks first — instant, no model needed
    if len(text.split()) < 3:
        return False  # too short
    if len(set(text.lower().replace(" ", ""))) < 4:
        return False  # repeated characters — spam

    # ML toxicity check for Malayalam/Manglish
    if state.toxicity_classifier:
        result = state.toxicity_classifier(text[:512])[0]
        if result["label"] == "Offensive":
            return False

    return True


@router.post("/submit", response_model=FeedbackItem)
def submit_feedback(
    req: FeedbackSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit feedback")

    # Content moderation
    if not is_appropriate(req.text):
        raise HTTPException(
            status_code=400,
            detail="Feedback flagged as inappropriate or too short. Please provide constructive feedback."
        )

    session_id = f"direct-{uuid.uuid4()}"
    db_session = DBSession(
        session_id=session_id,
        created_by=current_user.id,
        total_rows=1
    )
    db.add(db_session)

    item = DBFeedbackItem(
        item_id=0,
        session_id=session_id,
        text=req.text,
        department=req.department,
        subject=req.subject
    )
    db.add(item)
    db.commit()

    return FeedbackItem(
        id=0,
        text=req.text,
        department=req.department,
        subject=req.subject
    )