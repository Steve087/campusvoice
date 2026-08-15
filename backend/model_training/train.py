import sys
sys.path.append("..")

from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from torch.utils.data import DataLoader
import pandas as pd
import os

# --- Config ---
BASE_MODEL = "all-MiniLM-L6-v2"
OUTPUT_PATH = "../models/cec-feedback-model"
BATCH_SIZE = 16
EPOCHS = 10
WARMUP_STEPS = 10

# --- Load Data ---
df = pd.read_csv("training_data.csv")
print(f"Loaded {len(df)} training pairs")

# Split 80/20
train_df = df.sample(frac=0.8, random_state=42)
val_df = df.drop(train_df.index)

# --- Create InputExamples ---
train_examples = [
    InputExample(texts=[row["text1"], row["text2"]], label=float(row["label"]))
    for _, row in train_df.iterrows()
]

val_examples = [
    InputExample(texts=[row["text1"], row["text2"]], label=float(row["label"]))
    for _, row in val_df.iterrows()
]

# --- Model ---
model = SentenceTransformer(BASE_MODEL)

# --- DataLoader ---
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=BATCH_SIZE)

# --- Loss ---
# CosineSimilarityLoss — trains model to push similar pairs together
# and dissimilar pairs apart
train_loss = losses.CosineSimilarityLoss(model)

# --- Evaluator ---
sentences1 = [e.texts[0] for e in val_examples]
sentences2 = [e.texts[1] for e in val_examples]
scores = [e.label for e in val_examples]

evaluator = evaluation.EmbeddingSimilarityEvaluator(
    sentences1, sentences2, scores,
    name="cec-val"
)

# --- Train ---
os.makedirs(OUTPUT_PATH, exist_ok=True)

print(f"Training on {len(train_examples)} pairs...")
print(f"Validating on {len(val_examples)} pairs...")

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=EPOCHS,
    warmup_steps=WARMUP_STEPS,
    output_path=OUTPUT_PATH,
    evaluation_steps=50,
    save_best_model=True,
    show_progress_bar=True
)

print(f"\nModel saved to {OUTPUT_PATH}")