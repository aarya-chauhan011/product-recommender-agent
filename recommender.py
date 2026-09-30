import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
MODEL = "openai/gpt-oss-120b"
PROFILE_FILE = "profile.json"

with open("dataset/products.json", encoding="utf-8") as f:
    catalog = json.load(f)
categories = sorted({p["category"] for p in catalog})

# ---------- Profile save / load ----------
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"category": None, "max_budget": None,
            "liked_brands": [], "disliked_brands": [], "liked_features": []}

def save_profile():
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

profile = load_profile()

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

def update_profile(new):
    for key in ("category", "max_budget"):
        if new.get(key) is not None:
            profile[key] = new[key]
    for brand in new.get("liked_brands", []):
        if brand not in profile["liked_brands"]:
            profile["liked_brands"].append(brand)
        if brand in profile["disliked_brands"]:
            profile["disliked_brands"].remove(brand)
    for brand in new.get("disliked_brands", []):
        if brand not in profile["disliked_brands"]:
            profile["disliked_brands"].append(brand)
        if brand in profile["liked_brands"]:
            profile["liked_brands"].remove(brand)
    for feat in new.get("liked_features", []):
        if feat not in profile["liked_features"]:
            profile["liked_features"].append(feat)
    save_profile()

# ---------- Filter + Score ----------
def score(p):
    s = 0
    if str(p["brand"]).lower() in [b.lower() for b in profile["liked_brands"]]:
        s += 3
    for feat in profile["liked_features"]:
        if feat.lower() in str(p["description"]).lower() or feat.lower() in str(p["name"]).lower():
            s += 1
    return s

def find_products():
    results = []
    disliked = [b.lower() for b in profile["disliked_brands"]]
    for p in catalog:
        if profile["category"] and p["category"] != profile["category"]:
            continue
        if str(p["brand"]).lower() in disliked:
            continue
        if profile["max_budget"]:
            try:
                if float(p["price"]) > float(profile["max_budget"]):
                    continue
            except (ValueError, TypeError):
                pass
        results.append(p)
    results.sort(key=score, reverse=True)
    return results

# ---------- Chat loop ----------
history = []
print("Bot: Hi! What are you looking for today? (type 'quit' to exit, 'reset' to clear your saved preferences)")
print("Bot: I have Jewellery and Home Decor items available.")
if any(profile.values()):
    print("Bot: I remember your previous preferences:", profile)

while True:
    user = input("You: ")
    if user.lower() == "quit":
        break
    if user.lower() == "reset":
        profile = {"category": None, "max_budget": None, "liked_brands": [],
                   "disliked_brands": [], "liked_features": []}
        save_profile()
        print("Bot: All preferences have been cleared!")
        continue

    update_profile(extract_preferences(user))
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
    history.append({"role": "user", "content": user})
    reply = ask(system, history)
    history.append({"role": "assistant", "content": reply})
    print("Bot:", reply)
    print("[Profile]", profile)