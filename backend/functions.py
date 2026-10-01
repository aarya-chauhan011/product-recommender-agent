"""Core functions: catalog loading, user profile handling, filtering and scoring."""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_FILE = BASE_DIR / "dataset" / "products.json"
PROFILE_FILE = BASE_DIR / "profile.json"

# ---------- Catalog ----------
with open(CATALOG_FILE, encoding="utf-8") as f:
    catalog = json.load(f)
categories = sorted({p["category"] for p in catalog})


# ---------- Profile save / load ----------
def empty_profile():
    return {"category": None, "max_budget": None,
            "liked_brands": [], "disliked_brands": [], "liked_features": []}


def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return empty_profile()


profile = load_profile()


def save_profile():
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def reset_profile():
    profile.clear()
    profile.update(empty_profile())
    save_profile()


def update_profile(new):
    if not isinstance(new, dict):
        return
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