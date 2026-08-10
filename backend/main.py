from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import state
from database import create_tables
from routes import auth, upload, analyze, admin, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Database ready.")
    print("Loading embedding model...")
    state.model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model ready.")
    yield
    print("Shutting down.")


app = FastAPI(
    title="CampusVoice API",
    description="Anonymous student feedback analyzer",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(admin.router)
app.include_router(feedback.router)


@app.get("/")
def root():
    return {"status": "CampusVoice API is running"}