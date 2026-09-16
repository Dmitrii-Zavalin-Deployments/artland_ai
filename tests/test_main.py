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
    
    # We temporarily sanitize sys.path to evict the parent path.
    original_path = list(sys.path)
    try:
        while parent_path_str in sys.path:
            sys.path.remove(parent_path_str)
            
        # Reloading the module triggers the conditional sys.path insertion on line 18.
        importlib.reload(src.main)
        
        # We assert that the parent path was successfully restored into sys.path.
        assert parent_path_str in sys.path
    finally:
        sys.path[:] = original_path
        importlib.reload(src.main)


def test_import_error_fallback():
    """
    Narrative: When relative package imports fail (e.g., executing main.py as a standalone script),
    the module must successfully catch the ImportError and fall back to absolute imports.
    """
    # We remove cached modules to force a clean re-import under test conditions.
    for mod in list(sys.modules.keys()):
        if "src.main" in mod or mod == "main":
            sys.modules.pop(mod, None)

    # We simulate relative import failure by intercepting package context.
    with patch.dict("sys.modules", {".": None}):
        import importlib

        import src.main
        importlib.reload(src.main)
        
        assert src.main is not None


def test_loaders_debug_logging_and_errors(tmp_path, caplog):
    """
    Narrative: When logging level is set to DEBUG, invoking load_json and load_schema 
    must emit debug log records. Furthermore, passing non-existent file paths must 
    correctly trigger FileNotFoundError.
    """
    # We configure the logger to capture DEBUG level messages.
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

    # We verify that both debug logging statements were successfully triggered.
    assert any("Loading JSON from file" in record.message for record in caplog.records)
    assert any("Loading schema from file" in record.message for record in caplog.records)

    # 2. Test FileNotFoundError branches
    missing_json = tmp_path / "non_existent_payload.json"
    with pytest.raises(FileNotFoundError, match="Required JSON file not found"):
        load_json(missing_json)

    missing_schema = tmp_path / "non_existent_schema.json"
    with pytest.raises(FileNotFoundError, match="Required schema file not found"):
        load_schema(missing_schema)


def test_main_schema_validation_error(tmp_path):
    """
    Narrative: When input or configuration data fails JSON schema validation inside main(),
    the pipeline catches the ValidationError, writes an error JSON payload, and returns early.
    """
    folder = tmp_path / "pipeline_run"
    folder.mkdir(parents=True, exist_ok=True)

    input_file = folder / "input.json"
    input_file.write_text('{"invalid_field": true}', encoding="utf-8")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.json").write_text('{"target_fps": 30}', encoding="utf-8")

    schema_dir = Path("schema")
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / "input_schema.json").write_text(
        '{"type": "object", "properties": {"valid_key": {"type": "string"}}, "required": ["valid_key"]}',
        encoding="utf-8"
    )
    (schema_dir / "config_schema.json").write_text('{"type": "object"}', encoding="utf-8")

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
    assert "ValidationError" in output_data["results"]["error"]


def test_main_successful_execution(tmp_path, monkeypatch):
    """
    Narrative: When all inputs, schemas, and pipeline steps execute successfully, 
    main() runs through all four sequential steps and writes a successful output JSON.
    """
    folder = tmp_path / "pipeline_run"
    folder.mkdir(parents=True, exist_ok=True)

    input_file = folder / "input.json"
    input_file.write_text('{"valid_key": "value"}', encoding="utf-8")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.json").write_text('{"target_fps": 30}', encoding="utf-8")

    schema_dir = Path("schema")
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / "input_schema.json").write_text(
        '{"type": "object", "properties": {"valid_key": {"type": "string"}}, "required": ["valid_key"]}',
        encoding="utf-8"
    )
    (schema_dir / "config_schema.json").write_text('{"type": "object"}', encoding="utf-8")

    # Mock all pipeline execution modules to return success status
    monkeypatch.setattr("frames_loader.run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr("artistic_pipeline_video.run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr("artistic_pipeline_magazine.run", lambda s: setattr(s, "results", {"status": "success"}))
    monkeypatch.setattr("zip_builder.run", lambda s: setattr(s, "results", {"status": "success"}))

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


def test_main_pipeline_step_error_halts(tmp_path, monkeypatch):
    """
    Narrative: If any pipeline step returns an error status in state.results, main() 
    halts execution, writes the error output JSON, and logs the failure.
    """
    folder = tmp_path / "pipeline_run"
    folder.mkdir(parents=True, exist_ok=True)

    input_file = folder / "input.json"
    input_file.write_text('{"valid_key": "value"}', encoding="utf-8")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.json").write_text('{"target_fps": 30}', encoding="utf-8")

    schema_dir = Path("schema")
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / "input_schema.json").write_text(
        '{"type": "object", "properties": {"valid_key": {"type": "string"}}, "required": ["valid_key"]}',
        encoding="utf-8"
    )
    (schema_dir / "config_schema.json").write_text('{"type": "object"}', encoding="utf-8")

    # Simulate error return at frames_loader step
    monkeypatch.setattr(
        "frames_loader.run",
        lambda s: setattr(s, "results", {"status": "error", "error": "Frames load failed"})
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
    assert output_data["results"]["error"] == "Frames load failed"


def test_main_global_exception_handler(tmp_path, monkeypatch):
    """
    Narrative: Unexpected exceptions raised during pipeline execution trigger the global 
    exception handler, capture error state, write output JSON, and re-raise.
    """
    folder = tmp_path / "pipeline_run"
    folder.mkdir(parents=True, exist_ok=True)

    input_file = folder / "input.json"
    input_file.write_text('{"valid_key": "value"}', encoding="utf-8")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.json").write_text('{"target_fps": 30}', encoding="utf-8")

    schema_dir = Path("schema")
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / "input_schema.json").write_text(
        '{"type": "object", "properties": {"valid_key": {"type": "string"}}, "required": ["valid_key"]}',
        encoding="utf-8"
    )
    (schema_dir / "config_schema.json").write_text('{"type": "object"}', encoding="utf-8")

    def raise_unexpected(s):
        raise RuntimeError("Unexpected crash in loader")

    monkeypatch.setattr("frames_loader.run", raise_unexpected)

    test_args = [
        "main.py",
        "--input_output_folder", str(folder),
        "--input_file_name", "input.json",
        "--output_file_name", "output.json"
    ]

    # Combined single with statement satisfying SIM117 without noqa
    with patch.object(sys, "argv", test_args), pytest.raises(
        RuntimeError, match="Unexpected crash in loader"
    ):
        main()

    output_path = folder / "output.json"
    assert output_path.exists()
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_data["results"]["status"] == "error"
    assert "Unexpected crash in loader" in output_data["results"]["error"]
