from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import User, Session as DBSession, AnalysisResult
from models.schemas import UserOut
from services.auth import require_admin
import json

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