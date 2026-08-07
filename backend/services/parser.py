import csv
import io
from models.schemas import FeedbackItem


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