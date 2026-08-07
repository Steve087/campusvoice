import numpy as np
import hdbscan
from models.schemas import FeedbackItem, FeedbackCluster


def cluster_feedback(
    feedback: list[FeedbackItem],
    vectors: np.ndarray,
    min_cluster_size: int = 3
) -> tuple[list[FeedbackCluster], list[FeedbackItem]]:

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric="euclidean"
    )
    labels = clusterer.fit_predict(vectors)

    cluster_map: dict[int, list[FeedbackItem]] = {}
    for item, label in zip(feedback, labels):
        cluster_map.setdefault(int(label), []).append(item)

    noise = cluster_map.pop(-1, [])

    clusters = []
    for cluster_id, items in cluster_map.items():
        label = _get_label(items, vectors, feedback, cluster_id, labels)
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