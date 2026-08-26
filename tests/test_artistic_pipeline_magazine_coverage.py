# tests/test_artistic_pipeline_magazine_coverage.py
import pytest

import artistic_pipeline_magazine
from state import State


def set_all_processor_runs(monkeypatch, **overrides):
    """Helper to mock run methods across all magazine pipeline processors."""
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


def test_magazine_no_frames_raises_error(setup_pipeline_environment, tmp_path):
    """Covers line 43: ValueError when frame_paths is empty or missing."""
    state = State({}, {}, tmp_path)
    state.frame_paths = []

    with pytest.raises(ValueError, match="NO-DEFAULT POLICY VIOLATION: No frames found"):
        artistic_pipeline_magazine.run(state)


def test_magazine_same_file_path_handling(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers line 55: Same-file check where source and destination resolve identically."""
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
    """Covers lines 62, 68, 95, 103, 111, 119: AttributeError when processors lack a 'run' method."""
    external_frame = tmp_path / "external_frame.jpg"
    external_frame.write_bytes(b"dummy image data")

    state = State({}, {}, tmp_path)
    state.frame_paths = [external_frame]

    try:
        delattr(app, 'run')
    except AttributeError:
        pass
    # 1. artistic_painting_processor lacks run
    import processor.artistic_painting_processor as app
    monkeypatch.delattr(app, "run", raising=False)
    with pytest.raises(AttributeError, match="artistic_painting_processor.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 2. add_fading_edges lacks run
    monkeypatch.setattr(app, "run", lambda s: None)
    import processor.add_fading_edges as afe
    monkeypatch.delattr(afe, "run", raising=False)
    with pytest.raises(AttributeError, match="add_fading_edges.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 3. generate_background lacks run
    monkeypatch.setattr(afe, "run", lambda s: None)
    import processor.generate_background as gb
    monkeypatch.delattr(gb, "run", raising=False)
    with pytest.raises(AttributeError, match="generate_background.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 4. expand_image lacks run
    monkeypatch.setattr(gb, "run", lambda s: None)
    import processor.expand_image as ei
    monkeypatch.delattr(ei, "run", raising=False)
    with pytest.raises(AttributeError, match="expand_image.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 5. generate_photo_pdf lacks run
    monkeypatch.setattr(ei, "run", lambda s: None)
    import processor.generate_photo_pdf as gpdf
    monkeypatch.delattr(gpdf, "run", raising=False)
    with pytest.raises(AttributeError, match="generate_photo_pdf.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)

    # 6. generate_cover lacks run
    monkeypatch.setattr(gpdf, "run", lambda s: None)
    import processor.generate_cover as gcov
    monkeypatch.delattr(gcov, "run", raising=False)
    with pytest.raises(AttributeError, match="generate_cover.*lacks a 'run' method"):
        artistic_pipeline_magazine.run(state)


def test_working_file_missing_after_processing(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers line 74: FileNotFoundError when working frame is missing after processing."""
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
    """Covers line 124 (state.results = {} when None) and lines 129-135 (exception block)."""
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
