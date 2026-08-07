from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import FeedbackItem as DBFeedbackItem
from models.schemas import EmbedRequest, EmbedResponse
from services.embeddings import generate_embeddings
import state

router = APIRouter(prefix="/embed", tags=["embed"])


@router.post("/", response_model=EmbedResponse)
def embed_feedback(req: EmbedRequest, db: Session = Depends(get_db)):
    # 1. Load feedback from DB
    items = db.query(DBFeedbackItem).filter(
        DBFeedbackItem.session_id == req.session_id
    ).all()

    if not items:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Extract texts
    texts = [item.text for item in items]

    # 3. Generate vectors
    vectors = generate_embeddings(texts)

    # 4. Store in memory cache keyed by session_id
    state.vector_cache[req.session_id] = vectors

    return EmbedResponse(
        session_id=req.session_id,
        vectors_shape=list(vectors.shape),
        status="embedded"
    )