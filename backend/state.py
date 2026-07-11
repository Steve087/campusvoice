# backend/state.py

from sentence_transformers import SentenceTransformer

# This will hold the loaded model
# None until lifespan sets it at startup
model: SentenceTransformer | None = None