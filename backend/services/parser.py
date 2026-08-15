import csv
import io
from models.schemas import FeedbackItem


SYNONYMS = {
    "wifi": "internet",
    "wi-fi": "internet",
    "net": "internet",
    "network": "internet",
    "connection": "internet",
    "mess": "canteen",
    "food court": "canteen",
    "projector": "classroom equipment",
    "lab equipment": "classroom equipment",
    "faculty": "teacher",
    "prof": "teacher",
    "professor": "teacher",
    "lecturer": "teacher",
    "sir": "teacher",
    "madam": "teacher",
    "ma'am": "teacher",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    for word, replacement in SYNONYMS.items():
        text = text.replace(word, replacement)
    return text


def parse_csv(file_bytes: bytes) -> list[FeedbackItem]:
    content = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    items = []
    for i, row in enumerate(reader):
        if not row.get("text"):
            continue
        items.append(FeedbackItem(
            id=i,
            text=row["text"].strip(),
            department=row.get("department"),
            subject=row.get("subject"),
        ))

    return items


def parse_raw_text(text: str) -> list[FeedbackItem]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return [FeedbackItem(id=i, text=line) for i, line in enumerate(lines)]