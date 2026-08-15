from sentence_transformers import SentenceTransformer
import numpy as np

base_model = SentenceTransformer("all-MiniLM-L6-v2")
finetuned_model = SentenceTransformer("../models/cec-feedback-model")

TEST_PAIRS = [
    # Should be similar (score close to 1.0)
    ("wifi is bad", "internet not working", "similar"),
    ("canteen food is bad", "mess quality is poor", "similar"),
    ("teacher doesn't finish syllabus", "faculty skips portions", "similar"),

    # Should be different (score close to 0.0)
    ("wifi is bad", "canteen food is bad", "different"),
    ("library closes early", "internet is slow", "different"),
]

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"{'Pair':<50} {'Expected':<12} {'Base':<8} {'Finetuned'}")
print("-" * 85)

for t1, t2, expected in TEST_PAIRS:
    base_e1 = base_model.encode(t1)
    base_e2 = base_model.encode(t2)
    base_score = cosine_sim(base_e1, base_e2)

    ft_e1 = finetuned_model.encode(t1)
    ft_e2 = finetuned_model.encode(t2)
    ft_score = cosine_sim(ft_e1, ft_e2)

    label = f"{t1[:20]}... / {t2[:20]}..."
    print(f"{label:<50} {expected:<12} {base_score:.3f}    {ft_score:.3f}")