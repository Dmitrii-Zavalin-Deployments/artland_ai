# tests/test_artistic_pipeline_magazine_coverage.py
"""
Literate Test Suite: Artistic Pipeline Magazine Coverage & Edge Cases
====================================================================
Narrative verification ensuring absolute 100% test coverage across all branches,
path insertions, processor delegations, and error handling protocols.
"""

import sys
import importlib
from pathlib import Path
import pytest

import artistic_pipeline_magazine
from state import State


def set_all_processor_runs(monkeypatch, **overrides):
    """
    Narrative: Helper utility to mock execution entry points ('run') across 
    all sub-processors invoked during the magazine pipeline compilation stages.
    """
    import processor.add_fading_edges as afe
    import processor.artistic_painting_processor as app
    import processor.expand_image as ei
    import processor.generate_background as gb
    import processor.generate_cover as gcov
    import processor.generate_photo_pdf as gpdf

    monkeypatch.setattr(app, "run", overrides.get("app_run", lambda s: None))
    monkeypatch.setattr(afe, "run", overrides.get("afe_run", lambda s: None))
    monkeypatch.setattr(gb, "run", overrides.get("gb_run", lambda s: None))
    monkeypatch.setattr(ei, "run", overrides.get("ei_run", lambda s: None))
    monkeypatch.setattr(gpdf, "run", overrides.get("gpdf_run", lambda s: None))
    monkeypatch.setattr(gcov, "run", overrides.get("gcov_run", lambda s: None))


def test_sys_path_insertion_coverage():
    """
    Narrative: When the parent directory of artistic_pipeline_magazine is temporarily
    removed from sys.path, importing or reloading the module forces the execution 
    of the dynamic path insertion guard (Line 10), ensuring complete branch coverage.
    """
    parent_path_str = str(Path(artistic_pipeline_magazine.__file__).resolve().parent.parent)
    
    # We temporarily sanitize sys.path to evict the parent path.
    original_path = list(sys.path)
    try:
        while parent_path_str in sys.path:
            sys.path.remove(parent_path_str)
            
        # Reloading the module triggers the conditional sys.path insertion on line 10.
        importlib.reload(artistic_pipeline_magazine)
        
        # We assert that the parent path was successfully restored into sys.path.
        assert parent_path_str in sys.path
    finally:
        sys.path[:] = original_path
        importlib.reload(artistic_pipeline_magazine)


def test_magazine_no_frames_raises_error(setup_pipeline_environment, tmp_path):
    """
    Narrative: When state.frame_paths is empty or undefined, the magazine pipeline 
    must enforce the No-Default Policy by immediately raising a ValueError.
    """
    state = State({}, {}, tmp_path)
    state.frame_paths = []

    with pytest.raises(ValueError, match="NO-DEFAULT POLICY VIOLATION: No frames found"):
        artistic_pipeline_magazine.run(state)


def test_magazine_same_file_path_handling(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: When frame paths and working file paths resolve identically, 
    shutil.SameFileError is safely guarded and the compilation proceeds successfully.
    """
    original_dir = tmp_path / "original"
    original_dir.mkdir(parents=True, exist_ok=True)
    frame = original_dir / "sample.jpg"
    frame.write_bytes(b"dummy image data")

    state = State({}, {}, tmp_path)
    state.frame_paths = [frame]

    set_all_processor_runs(monkeypatch)
    artistic_pipeline_magazine.run(state)
    assert state.results["status"] == "success"


def test_missing_processor_run_methods(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: If any required sub-processor lacks a 'run' method, the pipeline 
    must raise an AttributeError upholding the No-Default Policy contract.
    """
    import processor.add_fading_edges as afe
    import processor.artistic_painting_processor as app
    import processor.expand_image as ei
    import processor.generate_background as gb
    import processor.generate_cover as gcov
    import processor.generate_photo_pdf as gpdf

    external_frame = tmp_path / "external_frame.jpg"
    external_frame.write_bytes(b"dummy image data")

    state = State({}, {}, tmp_path)
    state.frame_paths = [external_frame]

    # 1. artistic_painting_processor lacks run
    monkeypatch.delattr(app, "run", raising=False)
    with pytest.raises(AttributeError, match="artistic_painting_processor.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 2. add_fading_edges lacks run
    app.run = lambda s: None
    monkeypatch.delattr(afe, "run", raising=False)
    with pytest.raises(AttributeError, match="add_fading_edges.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 3. generate_background lacks run
    afe.run = lambda s: None
    monkeypatch.delattr(gb, "run", raising=False)
    with pytest.raises(AttributeError, match="generate_background.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 4. expand_image lacks run
    gb.run = lambda s: None
    monkeypatch.delattr(ei, "run", raising=False)
    with pytest.raises(AttributeError, match="expand_image.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 5. generate_photo_pdf lacks run
    ei.run = lambda s: None
    monkeypatch.delattr(gpdf, "run", raising=False)
    with pytest.raises(AttributeError, match="generate_photo_pdf.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 6. generate_cover lacks run
    gpdf.run = lambda s: None
    monkeypatch.delattr(gcov, "run", raising=False)
    with pytest.raises(AttributeError, match="generate_cover.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)


def test_working_file_missing_after_processing(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: If a processed working frame file is deleted or missing after processing steps,
    the pipeline must raise a FileNotFoundError in compliance with the No-Default Policy.
    """
    external_frame = tmp_path / "external_frame.jpg"
    external_frame.write_bytes(b"dummy image data")

    state = State({}, {}, tmp_path)
    state.frame_paths = [external_frame]

    def delete_working_file(s):
        if s.current_frame_path.exists():
            s.current_frame_path.unlink()

    set_all_processor_runs(monkeypatch, app_run=delete_working_file)

    with pytest.raises(FileNotFoundError, match="Processed working file missing"):
        artistic_pipeline_magazine.run(state)

    assert state.results["status"] == "error"


def test_results_none_initialization_and_exception_handling(setup_pipeline_environment, tmp_path, monkeypatch):
    """
    Narrative: When state.results is initialized to None, the pipeline must safely initialize
    it into a dictionary and capture unexpected exceptions into the error result state.
    """
    external_frame = tmp_path / "external_frame.jpg"
    external_frame.write_bytes(b"dummy image data")

    # Test successful path with results initialized to None
    state = State({}, {}, tmp_path)
    state.frame_paths = [external_frame]
    state.results = None

    set_all_processor_runs(monkeypatch)
    artistic_pipeline_magazine.run(state)
    assert state.results["status"] == "success"

    # Test exception handling block (e.g., TypeError during processing)
    state_err = State({}, {}, tmp_path)
    state_err.frame_paths = [external_frame]
    state_err.results = None

    def raise_type_error(s):
        raise TypeError("Simulated pipeline failure")

    set_all_processor_runs(monkeypatch, app_run=raise_type_error)

    with pytest.raises(TypeError, match="Simulated pipeline failure"):
        artistic_pipeline_magazine.run(state_err)

    assert state_err.results["status"] == "error"
    assert "Simulated pipeline failure" in state_err.results["error"]
