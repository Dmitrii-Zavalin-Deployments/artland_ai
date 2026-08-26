# tests/test_generate_cover_coverage.py
from pathlib import Path

import pytest
from PIL import Image

import processor.generate_cover as gc
from state import State


def test_get_extreme_colors_empty_pixels(tmp_path, monkeypatch):
    """Covers line 26: returns default colors when pixels list is empty."""
    img_path = tmp_path / "test.jpg"
    img = Image.new("RGB", (10, 10))
    img.save(img_path)

    class MockThumbnail:
        def getdata(self):
            return []

    class MockImage:
        def convert(self, mode):
            return self
        def resize(self, size):
            return MockThumbnail()

    monkeypatch.setattr(Image, "open", lambda p: MockImage())

    lightest, darkest = gc.get_extreme_colors(img_path)
    assert lightest == "rgb(255, 255, 255)"
    assert darkest == "rgb(0, 0, 0)"


def test_get_extreme_colors_exception(tmp_path):
    """Covers lines 43-47: exception handling when Image.open fails."""
    missing_path = tmp_path / "nonexistent.jpg"
    lightest, darkest = gc.get_extreme_colors(missing_path)
    assert lightest == "rgb(255, 255, 255)"
    assert darkest == "rgb(0, 0, 0)"


def test_run_missing_metadata(tmp_path):
    """Covers line 106: ValueError when required metadata fields are missing."""
    state = State({}, {}, tmp_path)
    state.book_to_publish_dir = tmp_path
    state.config = {"magazine_cover": {}}  # Empty metadata
    
    with pytest.raises(ValueError, match="NO-DEFAULT POLICY VIOLATION"):
        gc.run(state)


def test_run_bg_image_missing_and_results_none(tmp_path):
    """Covers line 116 (default colors when background image missing) and line 226 (state.results is None)."""
    state = State({}, {}, tmp_path)
    state.book_to_publish_dir = tmp_path
    state.results = None  # Triggers line 226: state.results = {}
    state.config = {
        "magazine_cover": {
            "title": "Test Title",
            "issue": "1",
            "tagline": "Test Tagline",
            "subtitle": "Test Subtitle",
            "author": "Test Author"
        }
    }

    # Ensure cover_background.jpg does NOT exist to trigger line 116
    bg_path = tmp_path / "cover_background.jpg"
    if bg_path.exists():
        bg_path.unlink()

    gc.run(state)

    assert state.results is not None
    assert "magazine_cover_path" in state.results
    assert Path(state.results["magazine_cover_path"]).exists()


def test_main_config_exists(tmp_path, monkeypatch):
    """Covers lines 232-242: main() execution when config/config.json exists."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.json"
    
    created_temp_config = False
    if not config_file.exists():
        config_file.write_text('{"magazine_cover": {"title": "T", "issue": "1", "tagline": "Tag", "subtitle": "Sub", "author": "Auth"}}', encoding="utf-8")
        created_temp_config = True

    try:
        monkeypatch.setattr(gc, "run", lambda s: setattr(s, "results", {"magazine_cover_path": str(tmp_path / "magazine_cover.html")}))
        gc.main()
    finally:
        if created_temp_config and config_file.exists():
            config_file.unlink()


def test_main_config_not_found(monkeypatch):
    """Covers lines 239-240: FileNotFoundError in main() when config.json does not exist."""
    monkeypatch.setattr(Path, "exists", lambda self: "config.json" not in str(self))
    
    with pytest.raises(FileNotFoundError, match="Production config not found"):
        gc.main()
