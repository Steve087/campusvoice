from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import FeedbackItem as DBFeedbackItem, Session as DBSession
from models.schemas import FeedbackSubmit, FeedbackItem
from services.auth import get_current_user
import uuid

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/submit", response_model=FeedbackItem)
def submit_feedback(
    req: FeedbackSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit feedback")

    # Find or create a direct-submission session for today
    session_id = f"direct-{uuid.uuid4()}"
    db_session = DBSession(
        session_id=session_id,
        created_by=current_user.id,
        total_rows=1
    )
    db.add(db_session)

    # Save feedback — no user id stored, anonymous
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