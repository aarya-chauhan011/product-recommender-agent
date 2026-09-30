"""Tests for profile handling, filtering and scoring."""
import pytest

from backend import functions as fn

SAMPLE_CATALOG = [
    {"name": "Gold Necklace", "brand": "Tanishq", "category": "Jewellery",
     "price": 20000, "description": "elegant gold necklace"},
    {"name": "Silver Ring", "brand": "Zoya", "category": "Jewellery",
     "price": 30000, "description": "silver ring with diamond"},
    {"name": "Vase", "brand": "HomeTown", "category": "Home Decor",
     "price": 1500, "description": "ceramic vase"},
    {"name": "Earrings", "brand": "Tanishq", "category": "Jewellery",
     "price": 8000, "description": "light gold earrings"},
]


@pytest.fixture
def sample_catalog(monkeypatch):
    monkeypatch.setattr(fn, "catalog", list(SAMPLE_CATALOG))


def names(products):
    return [p["name"] for p in products]


# ---------- Profile ----------
def test_empty_profile_shape():
    p = fn.empty_profile()
    assert p["category"] is None
    assert p["max_budget"] is None
    assert p["liked_brands"] == []


def test_update_profile_sets_category_and_budget():
    fn.update_profile({"category": "Jewellery", "max_budget": 25000})
    assert fn.profile["category"] == "Jewellery"
    assert fn.profile["max_budget"] == 25000


def test_update_profile_ignores_invalid_input():
    fn.update_profile("not a dict")
    fn.update_profile(None)
    assert fn.profile == fn.empty_profile()


def test_liked_brand_has_no_duplicates():
    fn.update_profile({"liked_brands": ["Tanishq"]})
    fn.update_profile({"liked_brands": ["Tanishq"]})
    assert fn.profile["liked_brands"] == ["Tanishq"]


def test_disliking_a_liked_brand_moves_it():
    fn.update_profile({"liked_brands": ["Zoya"]})
    fn.update_profile({"disliked_brands": ["Zoya"]})
    assert "Zoya" in fn.profile["disliked_brands"]
    assert "Zoya" not in fn.profile["liked_brands"]


def test_liking_a_disliked_brand_moves_it():
    fn.update_profile({"disliked_brands": ["Zoya"]})
    fn.update_profile({"liked_brands": ["Zoya"]})
    assert "Zoya" in fn.profile["liked_brands"]
    assert "Zoya" not in fn.profile["disliked_brands"]


def test_profile_is_saved_to_file(tmp_path):
    fn.update_profile({"category": "Home Decor"})
    assert (tmp_path / "profile.json").exists()


def test_reset_profile_clears_everything():
    fn.update_profile({"category": "Jewellery", "liked_brands": ["Zoya"]})
    fn.reset_profile()
    assert fn.profile == fn.empty_profile()


# ---------- Filtering ----------
def test_no_preferences_returns_everything(sample_catalog):
    assert len(fn.find_products()) == 4


def test_filter_by_category(sample_catalog):
    fn.update_profile({"category": "Jewellery"})
    results = fn.find_products()
    assert len(results) == 3
    assert all(p["category"] == "Jewellery" for p in results)


def test_filter_by_budget(sample_catalog):
    fn.update_profile({"category": "Jewellery", "max_budget": 25000})
    assert set(names(fn.find_products())) == {"Gold Necklace", "Earrings"}


def test_budget_given_as_string_works(sample_catalog):
    fn.update_profile({"max_budget": "10000"})
    assert set(names(fn.find_products())) == {"Earrings", "Vase"}


def test_disliked_brand_is_excluded(sample_catalog):
    fn.update_profile({"disliked_brands": ["zoya"]})  # case-insensitive
    assert "Silver Ring" not in names(fn.find_products())


def test_bad_price_value_does_not_crash(sample_catalog, monkeypatch):
    bad = {"name": "Mystery", "brand": "X", "category": "Jewellery",
           "price": "abc", "description": ""}
    monkeypatch.setattr(fn, "catalog", SAMPLE_CATALOG + [bad])
    fn.update_profile({"max_budget": 100})
    assert "Mystery" in names(fn.find_products())


# ---------- Scoring / ranking ----------
def test_liked_brand_ranks_first(sample_catalog):
    fn.update_profile({"category": "Jewellery", "liked_brands": ["Zoya"]})
    assert fn.find_products()[0]["name"] == "Silver Ring"


def test_liked_feature_boosts_ranking(sample_catalog):
    fn.update_profile({"category": "Jewellery", "liked_features": ["gold"]})
    top_two = names(fn.find_products())[:2]
    assert set(top_two) == {"Gold Necklace", "Earrings"}


def test_score_is_zero_without_preferences(sample_catalog):
    assert fn.score(SAMPLE_CATALOG[0]) == 0


def test_brand_score_is_three():
    fn.update_profile({"liked_brands": ["Tanishq"]})
    assert fn.score(SAMPLE_CATALOG[0]) == 3