import numpy as np
import state


def generate_embeddings(texts: list[str]) -> np.ndarray:
    return state.model.encode(texts, show_progress_bar=False)