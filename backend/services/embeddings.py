import numpy as np
import state


def generate_embeddings(texts: list[str]) -> np.ndarray:
    vectors = state.model.encode(texts, show_progress_bar=False)
    # Normalize — makes cosine distance work correctly
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms