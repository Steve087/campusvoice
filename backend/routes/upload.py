from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Session as DBSession, FeedbackItem as DBFeedbackItem
from models.schemas import UploadResponse
from services.parser import parse_csv
import uuid

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload_feedback(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    # 2. Read and parse
    contents = await file.read()
    items = parse_csv(contents)

    if not items:
        raise HTTPException(status_code=400, detail="No valid feedback rows found")

    # 3. Create session in DB
    session_id = str(uuid.uuid4())
    db_session = DBSession(
        session_id=session_id,
        created_by=1,  # hardcoded for now — will use JWT user later
        total_rows=len(items)
    )
    db.add(db_session)

    # 4. Save all feedback items to DB
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

    # 5. Return preview
    departments = list(set(i.department for i in items if i.department))
    return UploadResponse(
        session_id=session_id,
        total_rows=len(items),
        preview=[i.text for i in items[:5]],
        departments=departments
    )