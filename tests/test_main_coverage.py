# tests/test_main_coverage.py
import json
import pytest
from pathlib import Path

import main
from state import State


def test_main_schema_validation_failure(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 65-78: ValidationError handling during input/config schema validation."""
    # Write an invalid input file that violates input_schema.json (e.g., unexpected format or missing required fields)
    input_file = tmp_path / "project" / "invalid_input.json"
    input_file.write_text(json.dumps({"invalid_field": 123}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--input_output_folder",
            str(tmp_path / "project"),
            "--input_file_name",
            "invalid_input.json",
            "--output_file_name",
            "output.json",
        ],
    )

    main.main()

    output_json = tmp_path / "project" / "output.json"
    assert output_json.exists()
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert data["results"]["status"] == "error"
    assert "ValidationError" in data["results"]["error"] or len(data["results"]["error"]) > 0


def test_main_halt_at_frames_loader(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 87-90: Pipeline halt during step 1 (frames_loader)."""
    input_file = tmp_path / "project" / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": "dummy.zip"}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--input_output_folder",
            str(tmp_path / "project"),
            "--input_file_name",
            "input.json",
            "--output_file_name",
            "output.json",
        ],
    )

    import frames_loader
    def mock_frames_loader_error(state):
        state.results = {"status": "error", "error": "Frames loader failed"}

    monkeypatch.setattr(frames_loader, "run", mock_frames_loader_error)

    main.main()

    output_json = tmp_path / "project" / "output.json"
    assert output_json.exists()
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert data["results"]["status"] == "error"
    assert data["results"]["error"] == "Frames loader failed"


def test_main_halt_at_artistic_pipeline_video(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 95-98: Pipeline halt during step 2 (artistic_pipeline_video)."""
    input_file = tmp_path / "project" / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": "dummy.zip"}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--input_output_folder",
            str(tmp_path / "project"),
            "--input_file_name",
            "input.json",
            "--output_file_name",
            "output.json",
        ],
    )

    import frames_loader
    import artistic_pipeline_video

    monkeypatch.setattr(frames_loader, "run", lambda s: setattr(s, "results", {"status": "success"}))
    def mock_video_error(state):
        state.results = {"status": "error", "error": "Video pipeline failed"}
    monkeypatch.setattr(artistic_pipeline_video, "run", mock_video_error)

    main.main()

    output_json = tmp_path / "project" / "output.json"
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert data["results"]["status"] == "error"
    assert data["results"]["error"] == "Video pipeline failed"


def test_main_halt_at_artistic_pipeline_magazine(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 103-106: Pipeline halt during step 3 (artistic_pipeline_magazine)."""
    input_file = tmp_path / "project" / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": "dummy.zip"}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--input_output_folder",
            str(tmp_path / "project"),
            "--input_file_name",
            "input.json",
            "--output_file_name",
            "output.json",
        ],
    )

    import frames_loader
    import artistic_pipeline_video
    import artistic_pipeline_magazine

    monkeypatch.setattr(frames_loader, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(artistic_pipeline_video, "run", lambda s: setattr(s, "results", {"status": "success"}))
    def mock_magazine_error(state):
        state.results = {"status": "error", "error": "Magazine pipeline failed"}
    monkeypatch.setattr(artistic_pipeline_magazine, "run", mock_magazine_error)

    main.main()

    output_json = tmp_path / "project" / "output.json"
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert data["results"]["status"] == "error"
    assert data["results"]["error"] == "Magazine pipeline failed"


def test_main_halt_at_zip_builder(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 111-114: Pipeline halt during step 4 (zip_builder)."""
    input_file = tmp_path / "project" / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": "dummy.zip"}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--input_output_folder",
            str(tmp_path / "project"),
            "--input_file_name",
            "input.json",
            "--output_file_name",
            "output.json",
        ],
    )

    import frames_loader
    import artistic_pipeline_video
    import artistic_pipeline_magazine
    import zip_builder

    monkeypatch.setattr(frames_loader, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(artistic_pipeline_video, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(artistic_pipeline_magazine, "run", lambda s: setattr(s, "results", {"status": "success"}))
    def mock_zip_error(state):
        state.results = {"status": "error", "error": "ZIP builder failed"}
    monkeypatch.setattr(zip_builder, "run", mock_zip_error)

    main.main()

    output_json = tmp_path / "project" / "output.json"
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert data["results"]["status"] == "error"
    assert data["results"]["error"] == "ZIP builder failed"


def test_main_critical_exception_handling(setup_pipeline_environment, tmp_path, monkeypatch):
    """Covers lines 116-123: Critical exception handler and raise block in main()."""
    input_file = tmp_path / "project" / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": "dummy.zip"}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--input_output_folder",
            str(tmp_path / "project"),
            "--input_file_name",
            "input.json",
            "--output_file_name",
            "output.json",
        ],
    )

    import frames_loader
    def raise_runtime_error(state):
        raise RuntimeError("Unexpected catastrophic failure")

    monkeypatch.setattr(frames_loader, "run", raise_runtime_error)

    with pytest.raises(RuntimeError, match="Unexpected catastrophic failure"):
        main.main()

    output_json = tmp_path / "project" / "output.json"
    assert output_json.exists()
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert data["results"]["status"] == "error"
    assert "Unexpected catastrophic failure" in data["results"]["error"]
