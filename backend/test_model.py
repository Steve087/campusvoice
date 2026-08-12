from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="Hate-speech-CNERG/deoffxlmr-mono-malyalam"
)

tests = [
    "wifi adipoli illa",
    "canteen food waste aanu",
    "teacher nalla aanu padippikkan",
    "classroom dust falling making us sick",
    "wifi is terrible",
    "great faculty overall",
    "ith enth myr aan"
]

for text in tests:
    result = classifier(text)[0]
    print(f"{text[:45]:<45} → {result['label']} ({result['score']:.2f})")