# backend/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import state
from routes import upload, embed, analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # Runs once when server boots, before any request comes in
    print("Loading embedding model... this takes ~5 seconds")
    state.model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model ready.")

    yield  # server is now running and accepting requests

    # --- SHUTDOWN ---
    # Runs when you Ctrl+C the server
    print("Server shutting down.")


# Create the FastAPI app, pass lifespan so it runs on boot
app = FastAPI(
    title="CampusVoice API",
    description="Anonymous student feedback analyzer",
    lifespan=lifespan
)

# CORS — allows your React frontend to talk to this backend
# Without this, browsers block cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes — each file's router plugs in here
app.include_router(upload.router)
app.include_router(embed.router)
app.include_router(analyze.router)


# Health check — always useful, tells you server is alive
@app.get("/")
def root():
    return {"status": "CampusVoice API is running"}