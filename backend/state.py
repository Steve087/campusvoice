from sentence_transformers import SentenceTransformer
import numpy as np

model: SentenceTransformer | None = None
vector_cache: dict[str, np.ndarray] = {}