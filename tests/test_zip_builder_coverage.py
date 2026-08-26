# tests/test_zip_builder_coverage.py
from pathlib import Path

import pytest

import zip_builder as zb
from state import State


def test_zip_directory_not_found(tmp_path):
    """Covers line 14: FileNotFoundError when source_dir does not exist."""
    nonexistent = tmp_path / "nonexistent"
    zip_out = tmp_path / "out.zip"
    with pytest.raises(FileNotFoundError, match="Source directory for video photos not found"):
        zb.zip_directory(nonexistent, zip_out)


def test_zip_directory_empty(tmp_path):
    """Covers line 20: FileNotFoundError when source_dir is empty."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    zip_out = tmp_path / "out.zip"
    with pytest.raises(FileNotFoundError, match="is empty"):
        zb.zip_directory(empty_dir, zip_out)


def test_run_missing_processed_photos_zip_key(tmp_path):
    """Covers line 51: KeyError when processed_photos_zip_path is missing from state.inputs."""
    state = State({}, {}, tmp_path)
    with pytest.raises(KeyError, match="Required key 'processed_photos_zip_path' is missing"):
        zb.run(state)


def test_run_missing_magazine_assets_zip_key(tmp_path):
    """Covers line 66: KeyError when magazine_assets_zip_path is missing from state.inputs."""
    video_zip = tmp_path / "video.zip"
    state = State({"processed_photos_zip_path": str(video_zip)}, {}, tmp_path)
    
    # Create processed video dir with a file so ZIP 1 succeeds
    video_dir = tmp_path / "processed_video"
    video_dir.mkdir()
    (video_dir / "frame.jpg").touch()
    state.processed_dir_video = str(video_dir)

    with pytest.raises(KeyError, match="Required key 'magazine_assets_zip_path' is missing"):
        zb.run(state)


def test_run_publish_dir_not_found(tmp_path):
    """Covers line 76: FileNotFoundError when publish_dir does not exist."""
    video_zip = tmp_path / "video.zip"
    magazine_zip = tmp_path / "magazine.zip"
    state = State({
        "processed_photos_zip_path": str(video_zip),
        "magazine_assets_zip_path": str(magazine_zip)
    }, {}, tmp_path)

    video_dir = tmp_path / "processed_video"
    video_dir.mkdir()
    (video_dir / "frame.jpg").touch()
    state.processed_dir_video = str(video_dir)
    state.book_to_publish_dir = str(tmp_path / "nonexistent_publish")

    with pytest.raises(FileNotFoundError, match="Publication directory not found"):
        zb.run(state)


def test_run_missing_pdf_path(tmp_path):
    """Covers line 88: FileNotFoundError when magazine_content.pdf is missing."""
    video_zip = tmp_path / "video.zip"
    magazine_zip = tmp_path / "magazine.zip"
    state = State({
        "processed_photos_zip_path": str(video_zip),
        "magazine_assets_zip_path": str(magazine_zip)
    }, {}, tmp_path)

    video_dir = tmp_path / "processed_video"
    video_dir.mkdir()
    (video_dir / "frame.jpg").touch()
    state.processed_dir_video = str(video_dir)

    publish_dir = tmp_path / "publish"
    publish_dir.mkdir()
    state.book_to_publish_dir = str(publish_dir)

    with pytest.raises(FileNotFoundError, match="Magazine content PDF is missing"):
        zb.run(state)


def test_run_missing_bg_path(tmp_path):
    """Covers line 94: FileNotFoundError when cover_background.jpg is missing."""
    video_zip = tmp_path / "video.zip"
    magazine_zip = tmp_path / "magazine.zip"
    state = State({
        "processed_photos_zip_path": str(video_zip),
        "magazine_assets_zip_path": str(magazine_zip)
    }, {}, tmp_path)

    video_dir = tmp_path / "processed_video"
    video_dir.mkdir()
    (video_dir / "frame.jpg").touch()
    state.processed_dir_video = str(video_dir)

    publish_dir = tmp_path / "publish"
    publish_dir.mkdir()
    state.book_to_publish_dir = str(publish_dir)

    # Create PDF only
    (publish_dir / "magazine_content.pdf").touch()

    with pytest.raises(FileNotFoundError, match="Cover background image is missing"):
        zb.run(state)


def test_run_missing_html_path(tmp_path):
    """Covers line 100: FileNotFoundError when magazine_cover.html is missing."""
    video_zip = tmp_path / "video.zip"
    magazine_zip = tmp_path / "magazine.zip"
    state = State({
        "processed_photos_zip_path": str(video_zip),
        "magazine_assets_zip_path": str(magazine_zip)
    }, {}, tmp_path)

    video_dir = tmp_path / "processed_video"
    video_dir.mkdir()
    (video_dir / "frame.jpg").touch()
    state.processed_dir_video = str(video_dir)

    publish_dir = tmp_path / "publish"
    publish_dir.mkdir()
    state.book_to_publish_dir = str(publish_dir)

    # Create PDF and background, but miss HTML
    (publish_dir / "magazine_content.pdf").touch()
    (publish_dir / "cover_background.jpg").touch()

    with pytest.raises(FileNotFoundError, match="Magazine cover HTML is missing"):
        zb.run(state)


def test_run_success_with_none_results(tmp_path):
    """Covers line 121: initializes state.results = {} when state.results is None on success."""
    video_zip = tmp_path / "video.zip"
    magazine_zip = tmp_path / "magazine.zip"
    state = State({
        "processed_photos_zip_path": str(video_zip),
        "magazine_assets_zip_path": str(magazine_zip)
    }, {}, tmp_path)

    video_dir = tmp_path / "processed_video"
    video_dir.mkdir()
    (video_dir / "frame.jpg").touch()
    state.processed_dir_video = str(video_dir)

    publish_dir = tmp_path / "publish"
    publish_dir.mkdir()
    state.book_to_publish_dir = str(publish_dir)

    (publish_dir / "magazine_content.pdf").touch()
    (publish_dir / "cover_background.jpg").touch()
    (publish_dir / "magazine_cover.html").touch()

    state.results = None

    zb.run(state)

    assert state.results is not None
    assert state.results["status"] == "success"
    assert Path(state.results["processed_photos_zip_path"]).exists()
    assert Path(state.results["magazine_assets_zip_path"]).exists()


def test_run_exception_logging_and_results(tmp_path):
    """Covers lines 128-134: exception handler setting status='error' and recording error when state.results is None."""
    state = State({}, {}, tmp_path)
    state.results = None

    with pytest.raises(KeyError):
        zb.run(state)

    assert state.results is not None
    assert state.results["status"] == "error"
    assert "processed_photos_zip_path" in state.results["error"]
