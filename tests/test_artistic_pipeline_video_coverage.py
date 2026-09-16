# tests/test_artistic_pipeline_video_coverage.py
"""
Literate Test Suite: Artistic Pipeline Video Coverage & Edge Cases
==================================================================
Narrative verification ensuring absolute 100% test coverage across all branches,
path insertions, processor delegations, and error handling protocols for the 
video-ready photo pipeline.
"""

import importlib
import sys
from pathlib import Path

import pytest

import artistic_pipeline_video
from state import State


def test_sys_path_insertion_coverage():
    """
    Narrative: When the parent directory of artistic_pipeline_video is temporarily
    removed from sys.path, importing or reloading the module forces the execution 
    of the dynamic path insertion guard (Line 10), ensuring complete branch coverage.
    """
    parent_path_str = str(Path(artistic_pipeline_video.__file__).resolve().parent.parent)
    
    # We temporarily sanitize sys.path to evict the parent path.
    original_path = list(sys.path)
    try:
        while parent_path_str in sys.path:
            sys.path.remove(parent_path_str)
            
        # Reloading the module triggers the conditional sys.path insertion.
        importlib.reload(artistic_pipeline_video)
        
        # We assert that the parent path was successfully restored into sys.path.
        assert parent_path_str in sys.path
    finally:
        sys.path[:] = original_path
        importlib.reload(artistic_pipeline_video)


def test_video_pipeline_no_frames_raises_value_error(setup_pipeline_environment, tmp_path):
    """
    Narrative: When state.frame_paths is empty or undefined, the video pipeline 
    must enforce the No-Default Policy by immediately raising a ValueError.
    """
    state = State({}, {}, tmp_path)
    state.frame_paths = []

    with pytest.raises(ValueError, match="NO-DEFAULT POLICY VIOLATION: No frames found"):
        artistic_pipeline_video.run(state)


def test_video_pipeline_different_and_same_file_copy(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: The pipeline correctly handles both external frames (triggering shutil.copy)
    and internal frames where source and destination resolve identically, preventing SameFileErrors.
    """
    # 1. External frame path (triggers shutil.copy to working directory)
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

    # 2. Frame path already inside original_dir (bypasses shutil.copy via same-file resolution guard)
    internal_frame = state.original_dir / "internal.jpg"
    internal_frame.write_bytes(b"dummy image content")

    state_internal = State({}, {}, tmp_path)
    state_internal.frame_paths = [internal_frame]

    artistic_pipeline_video.run(state_internal)
    assert state_internal.results["status"] == "success"


def test_video_pipeline_missing_processor_run_attribute(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: If the artistic_painting_processor lacks a 'run' method, the pipeline 
    must raise an AttributeError upholding the No-Default Policy contract.
    """
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]

    import processor.artistic_painting_processor as app
    monkeypatch.delattr(app, "run", raising=False)

    with pytest.raises(AttributeError, match="artistic_painting_processor.*lacks a 'run' method"):
        artistic_pipeline_video.run(state)


def test_video_pipeline_missing_working_file_raises_file_not_found(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: If a processed working frame file is deleted or missing after processing steps,
    the pipeline must raise a FileNotFoundError in compliance with the No-Default Policy.
    """
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]

    import processor.artistic_painting_processor as app
    
    def corrupt_run(s):
        if s.current_frame_path.exists():
            s.current_frame_path.unlink()

    monkeypatch.setattr(app, "run", corrupt_run)

    with pytest.raises(FileNotFoundError, match="Artistic painting processor failed to generate output"):
        artistic_pipeline_video.run(state)

    assert state.results["status"] == "error"


def test_video_pipeline_results_none_initialization(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: When state.results is initialized to None, the pipeline must safely initialize
    it into a dictionary upon successful completion.
    """
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
    """
    Narrative: The global exception handler captures unexpected runtime errors, initializes
    missing result dictionaries, and correctly logs the critical pipeline halt.
    """
    frame = tmp_path / "sample.jpg"
    frame.write_bytes(b"dummy image content")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]
    state.results = None  # Test results initialization inside exception block

    import processor.artistic_painting_processor as app
    def raise_runtime_error(s):
        raise RuntimeError("Simulated video pipeline crash")

    monkeypatch.setattr(app, "run", raise_runtime_error)

    with pytest.raises(RuntimeError, match="Simulated video pipeline crash"):
        artistic_pipeline_video.run(state)

    assert state.results["status"] == "error"
    assert "Simulated video pipeline crash" in state.results["error"]
