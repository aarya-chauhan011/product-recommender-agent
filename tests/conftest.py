"""Shared test setup: tests never touch the real profile.json."""
import pytest

from backend import functions as fn


@pytest.fixture(autouse=True)
def isolated_profile(tmp_path, monkeypatch):
    # Save file ko temp folder me bhej do
    monkeypatch.setattr(fn, "PROFILE_FILE", tmp_path / "profile.json")

    # Asli profile ki copy rakho, test ke baad wapas daal denge
    original = {k: (list(v) if isinstance(v, list) else v) for k, v in fn.profile.items()}
    fn.profile.clear()
    fn.profile.update(fn.empty_profile())

    yield

    fn.profile.clear()
    fn.profile.update(original)