import numpy as np
import hdbscan
from models.schemas import FeedbackItem, FeedbackCluster


def deduplicate(feedback: list[FeedbackItem]) -> list[FeedbackItem]:
    seen = set()
    unique = []
    for item in feedback:
        normalized = item.text.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(item)
    return unique


def cluster_feedback(
    feedback: list[FeedbackItem],
    vectors: np.ndarray,
    min_cluster_size: int = 3
) -> tuple[list[FeedbackCluster], list[FeedbackItem]]:

    # Deduplicate before clustering
    unique_feedback = deduplicate(feedback)
    unique_texts = [item.text.strip().lower() for item in unique_feedback]

    # Map unique texts back to vectors
    text_to_idx = {item.text.strip().lower(): i for i, item in enumerate(feedback)}
    unique_indices = [text_to_idx[text] for text in unique_texts]
    unique_vectors = vectors[unique_indices]

    # Need at least min_cluster_size points
    if len(unique_feedback) < min_cluster_size:
        return [], unique_feedback

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=2,
        metric="cosine",
        cluster_selection_method="eom",
        cluster_selection_epsilon=0.15
    )
    labels = clusterer.fit_predict(unique_vectors)

    # Group by cluster label
    cluster_map: dict[int, list[FeedbackItem]] = {}
    for item, label in zip(unique_feedback, labels):
        cluster_map.setdefault(int(label), []).append(item)

    noise = cluster_map.pop(-1, [])

    clusters = []
    for cluster_id, items in cluster_map.items():
        label = _get_label(items, unique_vectors, unique_feedback, cluster_id, labels)
        clusters.append(FeedbackCluster(
            cluster_id=cluster_id,
            label=label,
            size=len(items),
            items=items,
            sentiment_score=0.0,
            is_urgent=False
        ))

    clusters.sort(key=lambda c: len(c.items), reverse=True)
    return clusters, noise


def _get_label(
    items: list[FeedbackItem],
    vectors: np.ndarray,
    all_feedback: list[FeedbackItem],
    cluster_id: int,
    labels: np.ndarray
) -> str:
    indices = [i for i, l in enumerate(labels) if l == cluster_id]
    centroid = vectors[indices].mean(axis=0)
    distances = np.linalg.norm(vectors[indices] - centroid, axis=1)
    closest = indices[np.argmin(distances)]
    return all_feedback[closest].text