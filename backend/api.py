"""FastAPI layer for the product recommender agent."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.functions import profile, reset_profile
from backend.orchestrator import chat

app = FastAPI(title="Product Recommender Agent")

# Frontend ko API call karne dene ke liye
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


@app.get("/")
def home():
    return {"status": "ok", "message": "Product Recommender Agent API"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    reply = chat(req.message, history)
    return ChatResponse(reply=str(reply), profile=profile)


@app.get("/profile")
def get_profile():
    return profile


@app.post("/reset")
def reset():
    reset_profile()
    history.clear()
    return {"message": "All preferences have been cleared!"}