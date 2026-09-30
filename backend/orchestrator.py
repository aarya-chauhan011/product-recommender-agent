"""Orchestrator: all LLM (Groq) calls and the agent flow."""
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from backend.functions import categories, profile, find_products, update_profile

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = Groq()
MODEL = "openai/gpt-oss-120b"


# ---------- LLM helper ----------
def ask(system, messages, max_tokens=800):
    r = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}] + messages,
    )
    return r.choices[0].message.content


# ---------- Agent 1: Preference Agent ----------
def extract_preferences(user_msg):
    system = (
        "Extract shopping preferences from the message. Return ONLY JSON: "
        '{"category": null, "max_budget": null, "liked_brands": [], '
        '"disliked_brands": [], "liked_features": []}. '
        f"category must be one of {categories} or null. "
        "max_budget is a number or null. "
        "liked_features are short single words (e.g. gold, silver, wooden, wall, ring). "
        "Use null or empty list if not mentioned. Return ONLY the JSON, nothing else."
    )
    text = ask(system, [{"role": "user", "content": user_msg}], 250)
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


# ---------- Agent 2: Recommendation Agent ----------
def chat(user_msg, history):
    """Run one chat turn: update profile, find products, get the LLM reply.

    `history` is a list of {"role", "content"} dicts and is updated in place.
    """
    update_profile(extract_preferences(user_msg))
    matches = find_products()

    system = (
        "You are a friendly shopping assistant. Always reply in English, using plain "
        "English words and the Latin alphabet only. Never reply in Hindi, Devanagari "
        "script, or any other language. "
        "Recommend ONLY from the matching products below (already ranked best first). "
        "For each pick, briefly say why it fits the user's saved preferences. "
        "If category or budget is unknown, ask one short question. "
        "If nothing matches, say so honestly.\n"
        f"Saved user profile: {json.dumps(profile)}\n"
        f"Ranked matching products: {json.dumps(matches[:3])}"
    )
    history.append({"role": "user", "content": user_msg})
    reply = ask(system, history)
    history.append({"role": "assistant", "content": reply})
    return reply