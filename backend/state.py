from sentence_transformers import SentenceTransformer
from transformers import pipeline
import numpy as np

model: SentenceTransformer | None = None
vector_cache: dict[str, np.ndarray] = {}
toxicity_classifier = None