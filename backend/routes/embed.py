from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import FeedbackItem as DBFeedbackItem
from models.schemas import EmbedRequest, EmbedResponse
from services.embeddings import generate_embeddings
from services.auth import require_admin
import state

router = APIRouter(prefix="/embed", tags=["embed"])


@router.post("/", response_model=EmbedResponse)
def embed_feedback(
    req: EmbedRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    items = db.query(DBFeedbackItem).filter(
        DBFeedbackItem.session_id == req.session_id
    ).all()

    if not items:
        raise HTTPException(status_code=404, detail="Session not found")

    texts = [item.text for item in items]
    vectors = generate_embeddings(texts)
    state.vector_cache[req.session_id] = vectors

    return EmbedResponse(
        session_id=req.session_id,
        vectors_shape=list(vectors.shape),
        status="embedded"
    )