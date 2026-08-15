import numpy as np
import state
from services.parser import normalize_text


def generate_embeddings(texts: list[str]) -> np.ndarray:
    # Normalize synonyms before embedding
    normalized = [normalize_text(t) for t in texts]
    vectors = state.model.encode(normalized, show_progress_bar=False)
    # Normalize vectors for cosine distance
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms