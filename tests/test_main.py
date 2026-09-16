# tests/test_main.py
"""
Literate Test Suite: Artland AI Main Pipeline Coverage & Edge Cases
===================================================================
Narrative verification ensuring absolute 100% test coverage across dynamic path insertions,
import fallbacks, JSON/schema loaders, schema validation errors, pipeline step error halts,
and global exception handlers.
"""

import importlib
import json
import logging
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

import src.main
from src.main import load_json, load_schema, main


def test_sys_path_insertion_coverage():
    """
    Narrative: When the parent directory of src.main is temporarily removed from sys.path,
    reloading the module forces the execution of the dynamic path insertion guard (Line 18),
    ensuring complete branch coverage.
    """
    parent_path_str = str(Path(src.main.__file__).resolve().parent.parent)
    
    original_path = list(sys.path)
    try:
        while parent_path_str in sys.path:
            sys.path.remove(parent_path_str)
            
        importlib.reload(src.main)
        assert parent_path_str in sys.path
    finally:
        sys.path[:] = original_path
        importlib.reload(src.main)


def test_import_error_fallback():
    """
    Narrative: When relative package imports fail (e.g., executing main.py as a standalone script),
    the module must successfully catch the ImportError and fall back to absolute imports.
    """
    orig_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level > 0:
            raise ImportError("Simulated relative import failure")
        return orig_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=mock_import):
        importlib.reload(src.main)
        assert src.main is not None

    importlib.reload(src.main)


def test_loaders_debug_logging_and_errors(tmp_path, caplog):
    """
    Narrative: When logging level is set to DEBUG, invoking load_json and load_schema 
    must emit debug log records. Furthermore, passing non-existent file paths must 
    correctly trigger FileNotFoundError.
    """
    caplog.set_level(logging.DEBUG, logger="src.main")

    # 1. Test successful loading with debug logs
    json_file = tmp_path / "test_payload.json"
    json_file.write_text('{"key": "value"}', encoding="utf-8")

    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text('{"type": "object"}', encoding="utf-8")

    data = load_json(json_file)
    assert data == {"key": "value"}

    schema = load_schema(schema_file)
    assert schema == {"type": "object"}

    assert any("Loading JSON from file" in record.message for record in caplog.records)
    assert any("Loading schema from file" in record.message for record in caplog.records)

    # 2. Test FileNotFoundError branches
    missing_json = tmp_path / "non_existent_payload.json"
    with pytest.raises(FileNotFoundError, match="Required JSON file not found"):
        load_json(missing_json)

    missing_schema = tmp_path / "non_existent_schema.json"
    with pytest.raises(FileNotFoundError, match="Required schema file not found"):
        load_schema(missing_schema)


def _setup_test_environment(tmp_path, monkeypatch):
    """Helper fixture to set up isolated test directories in tmp_path."""
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "pipeline_run"
    folder.mkdir(parents=True, exist_ok=True)

    dummy_zip = folder / "dummy.zip"
    with zipfile.ZipFile(dummy_zip, "w") as zf:
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
            b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        zf.writestr("frame_01.png", png_bytes)

    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.json").write_text('{"target_fps": 30, "artistic_painting": {}}', encoding="utf-8")

    schema_dir = tmp_path / "schema"
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / "input_schema.json").write_text(
        '{"type": "object", "properties": {"valid_key": {"type": "string"}}, "required": ["valid_key"]}',
        encoding="utf-8"
    )
    (schema_dir / "config_schema.json").write_text('{"type": "object"}', encoding="utf-8")

    return folder, dummy_zip


def test_main_schema_validation_error(tmp_path, monkeypatch):
    """
    Narrative: When input data fails JSON schema validation inside main(),
    the pipeline catches ValidationError, writes an error JSON payload, and returns early.
    """
    folder, dummy_zip = _setup_test_environment(tmp_path, monkeypatch)

    input_file = folder / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "invalid_field": True}), encoding="utf-8")

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
    assert "required property" in output_data["results"]["error"]


def test_main_json_decode_error(tmp_path, monkeypatch):
    """
    Narrative: When input.json is malformed, json.JSONDecodeError is caught,
    and an error output JSON is written.
    """
    folder, _ = _setup_test_environment(tmp_path, monkeypatch)

    input_file = folder / "input.json"
    input_file.write_text("INVALID_JSON_PAYLOAD", encoding="utf-8")

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"


def test_main_logging_handlers_branch(tmp_path, monkeypatch):
    """
    Narrative: Triggers basicConfig setup inside main() when logging handlers list is empty.
    """
    folder, dummy_zip = _setup_test_environment(tmp_path, monkeypatch)
    input_file = folder / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "valid_key": "value"}), encoding="utf-8")

    monkeypatch.setattr(src.main.frames_loader, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(src.main.artistic_pipeline_video, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(src.main.artistic_pipeline_magazine, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(src.main.zip_builder, "run", lambda s: setattr(s, "results", {"status": "success"}))

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    root_logger = logging.getLogger()
    saved_handlers = list(root_logger.handlers)
    root_logger.handlers.clear()
    try:
        with patch.object(sys, "argv", test_args):
            main()
    finally:
        root_logger.handlers = saved_handlers


def test_main_successful_execution(tmp_path, monkeypatch):
    """
    Narrative: When all inputs, schemas, and pipeline steps execute successfully, 
    main() runs through all four sequential steps and writes a successful output JSON.
    """
    folder, dummy_zip = _setup_test_environment(tmp_path, monkeypatch)

    input_file = folder / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "valid_key": "value"}), encoding="utf-8")

    monkeypatch.setattr(src.main.frames_loader, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(src.main.artistic_pipeline_video, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(src.main.artistic_pipeline_magazine, "run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr(src.main.zip_builder, "run", lambda s: setattr(s, "results", {"status": "success"}))

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "success"


@pytest.mark.parametrize("failed_step", [1, 2, 3, 4])
def test_main_pipeline_step_error_halts(tmp_path, monkeypatch, failed_step):
    """
    Narrative: If any pipeline step returns an error status in state.results, main() 
    halts execution at that specific step, writes the error output JSON, and logs failure.
    """
    folder, dummy_zip = _setup_test_environment(tmp_path, monkeypatch)

    input_file = folder / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "valid_key": "value"}), encoding="utf-8")

    monkeypatch.setattr(
        src.main.frames_loader,
        "run",
        lambda s: setattr(s, "results", {"status": "error", "error": "Step 1 fail"} if failed_step == 1 else {"status": "success"})
    )
    monkeypatch.setattr(
        src.main.artistic_pipeline_video,
        "run",
        lambda s: setattr(s, "results", {"status": "error", "error": "Step 2 fail"} if failed_step == 2 else {"status": "success"})
    )
    monkeypatch.setattr(
        src.main.artistic_pipeline_magazine,
        "run",
        lambda s: setattr(s, "results", {"status": "error", "error": "Step 3 fail"} if failed_step == 3 else {"status": "success"})
    )
    monkeypatch.setattr(
        src.main.zip_builder,
        "run",
        lambda s: setattr(s, "results", {"status": "error", "error": "Step 4 fail"} if failed_step == 4 else {"status": "success"})
    )

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
    assert f"Step {failed_step} fail" in output_data["results"]["error"]


def test_main_global_exception_handler(tmp_path, monkeypatch):
    """
    Narrative: Unexpected exceptions raised during pipeline execution trigger the global 
    exception handler, capture error state, write output JSON, and re-raise.
    """
    folder, dummy_zip = _setup_test_environment(tmp_path, monkeypatch)

    input_file = folder / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "valid_key": "value"}), encoding="utf-8")

    def raise_unexpected(s):
        raise RuntimeError("Unexpected crash in loader")

    monkeypatch.setattr(src.main.frames_loader, "run", raise_unexpected)

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args), pytest.raises(
        RuntimeError, match="Unexpected crash in loader"
    ):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
    assert "Unexpected crash in loader" in output_data["results"]["error"]


def test_main_global_exception_handler_uninitialized_state(tmp_path, monkeypatch):
    """
    Narrative: Ensures exception handler branch handling missing or None state.results is covered.
    """
    folder, dummy_zip = _setup_test_environment(tmp_path, monkeypatch)

    input_file = folder / "input.json"
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "valid_key": "value"}), encoding="utf-8")

    def crash_and_wipe_results(s):
        s.results = None
        raise RuntimeError("Crash with null results")

    monkeypatch.setattr(src.main.frames_loader, "run", crash_and_wipe_results)

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    with patch.object(sys, "argv", test_args), pytest.raises(
        RuntimeError, match="Crash with null results"
    ):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
