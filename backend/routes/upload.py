from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Session as DBSession, FeedbackItem as DBFeedbackItem
from models.schemas import UploadResponse
from services.parser import parse_csv
from services.auth import get_current_user, require_admin
import uuid

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload_feedback(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # ← only admins can upload
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    contents = await file.read()
    items = parse_csv(contents)

    if not items:
        raise HTTPException(status_code=400, detail="No valid feedback rows found")

    session_id = str(uuid.uuid4())
    db_session = DBSession(
        session_id=session_id,
        created_by=current_user.id,  # ← now uses real user id from token
        total_rows=len(items)
    )
    db.add(db_session)

    for item in items:
        db_item = DBFeedbackItem(
            item_id=item.id,
            session_id=session_id,
            text=item.text,
            department=item.department,
            subject=item.subject
        )
        db.add(db_item)

    db.commit()

    departments = list(set(i.department for i in items if i.department))
    return UploadResponse(
        session_id=session_id,
        total_rows=len(items),
        preview=[i.text for i in items[:5]],
        departments=departments
    )