from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models.schemas import FeedbackItem, FeedbackCluster

analyzer = SentimentIntensityAnalyzer()
URGENT_THRESHOLD = -0.3


def score_text(text: str) -> float:
    return analyzer.polarity_scores(text)["compound"]


def analyze_sentiment(
    clusters: list[FeedbackCluster],
    noise: list[FeedbackItem]
) -> tuple[list[FeedbackCluster], list[FeedbackItem], list[FeedbackItem], dict[str, float]]:

    urgent_items: list[FeedbackItem] = []
    dept_scores: dict[str, list[float]] = {}

    for cluster in clusters:
        item_scores = []
        for item in cluster.items:
            score = score_text(item.text)
            item_scores.append(score)
            if item.department:
                dept_scores.setdefault(item.department, []).append(score)
            if score < URGENT_THRESHOLD:
                urgent_items.append(item)
                
            

        avg = sum(item_scores) / len(item_scores)
        cluster.sentiment_score = round(avg, 3)
        cluster.is_urgent = avg < URGENT_THRESHOLD

    urgent_texts = {item.text.strip().lower() for item in urgent_items}

    for item in noise:
        score = score_text(item.text)
        if item.department:
            dept_scores.setdefault(item.department, []).append(score)
        if score < URGENT_THRESHOLD:
            urgent_items.append(item)
            urgent_texts.add(item.text.strip().lower())


# Deduplicate urgent items by normalized text
    seen_urgent = set()
    unique_urgent = []
    for item in urgent_items:
        key = item.text.strip().lower()
        if key not in seen_urgent:
            seen_urgent.add(key)
            unique_urgent.append(item)
            urgent_items = unique_urgent
    # Remove urgent items from noise
    filtered_noise = [
        item for item in noise
        if item.text.strip().lower() not in urgent_texts
    ]

    dept_sentiments = {
        dept: round(sum(scores) / len(scores), 3)
        for dept, scores in dept_scores.items()
    }

    

    return clusters, urgent_items, filtered_noise, dept_sentiments