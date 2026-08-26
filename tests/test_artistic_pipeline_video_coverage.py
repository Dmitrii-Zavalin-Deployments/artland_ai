# tests/test_artistic_pipeline_video_coverage.py
from pathlib import Path
import pytest

import artistic_pipeline_video
from state import State


def test_video_pipeline_no_frames_raises_value_error(setup_pipeline_environment, tmp_path):
    """Covers line 34: ValueError when frame_paths is empty or missing."""
    state = State({}, {}, tmp_path)
    state.frame_paths = []

    with pytest.raises(ValueError, match="NO-DEFAULT POLICY VIOLATION: No frames found"):
        artistic_pipeline_video.run(state)


def test_video_pipeline_different_and_same_file_copy(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers line 43: shutil.copy execution when source and destination are distinct."""
    # 1. External frame path (triggers shutil.copy)
    external_dir = tmp_path / "external_source"
    external_dir.mkdir(parents=True, exist_ok=True)
    external_frame = external_dir / "sample.jpg"
    external_frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [external_frame]

    import processor.artistic_painting_processor as app
    monkeypatch.setattr(app, "run", lambda s: s.current_frame_path.write_bytes(b"processed content"))

    artistic_pipeline_video.run(state)
    assert state.results["status"] == "success"

    # 2. Frame path already inside original_dir (bypasses shutil.copy / same-file resolution)
    internal_frame = state.original_dir / "internal.jpg"
    internal_frame.write_bytes(b"dummy image content")

    state_internal = State({}, {}, tmp_path)
    state_internal.frame_paths = [internal_frame]

    artistic_pipeline_video.run(state_internal)
    assert state_internal.results["status"] == "success"


def test_video_pipeline_missing_processor_run_attribute(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers line 50: AttributeError when artistic_painting_processor lacks a 'run' method."""
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]

    import processor.artistic_painting_processor as app
    monkeypatch.delattr(app, "run", raising=False)

    with pytest.raises(AttributeError, match="artistic_painting_processor.*lacks a 'run' method"):
        artistic_pipeline_video.run(state)


def test_video_pipeline_missing_working_file_raises_file_not_found(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers line 57: FileNotFoundError when processor fails to create the output file."""
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]

    import processor.artistic_painting_processor as app
    # Processor runs but deletes/fails to generate the working file
    def corrupt_run(s):
        if s.current_frame_path.exists():
            s.current_frame_path.unlink()

    monkeypatch.setattr(app, "run", corrupt_run)

    with pytest.raises(FileNotFoundError, match="Artistic painting processor failed to generate output"):
        artistic_pipeline_video.run(state)

    assert state.results["status"] == "error"


def test_video_pipeline_results_none_initialization(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers line 71: Initializes state.results to {} when it is explicitly None on success."""
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]
    state.results = None  # Force None to test initialization branch

    import processor.artistic_painting_processor as app
    monkeypatch.setattr(app, "run", lambda s: s.current_frame_path.write_bytes(b"processed"))

    artistic_pipeline_video.run(state)
    assert state.results["status"] == "success"
    assert state.results["error"] == ""


def test_video_pipeline_exception_handling_block(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 76-82: Global exception handler, error state capture, and logging."""
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]
    state.results = None  # Test results initialization inside exception block (line 77-78)

    import processor.artistic_painting_processor as app
    def raise_runtime_error(s):
        raise RuntimeError("Simulated video pipeline crash")

    monkeypatch.setattr(app, "run", raise_runtime_error)

    with pytest.raises(RuntimeError, match="Simulated video pipeline crash"):
        artistic_pipeline_video.run(state)

    assert state.results["status"] == "error"
    assert "Simulated video pipeline crash" in state.results["error"]
