"""FastAPI layer for the product recommender agent."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.functions import profile, reset_profile, find_products
from backend.orchestrator import chat

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Product Recommender Agent")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple version: ek hi user ki conversation history
history = []


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    profile: dict
    products: list = []


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "templates" / "index.html")


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    reply = chat(req.message, history)
    return ChatResponse(
        reply=str(reply),
        profile=profile,
        products=find_products()[:3],
    )


@app.get("/profile")
def get_profile():
    return profile


@app.post("/reset")
def reset():
    reset_profile()
    history.clear()
    return {"message": "All preferences have been cleared!"}