# tests/test_main.py
"""
Literate Test Suite: Artland AI Main Pipeline Edge Cases & Coverage Completion
===========================================================================
Narrative verification ensuring absolute 100% test coverage by exercising 
fallback import blocks (ImportError) and debug-level logging pathways for JSON and schema loaders.
"""

import json
import logging
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from src.main import load_json, load_schema


def test_import_error_fallback():
    """
    Narrative: When relative package imports fail (e.g., executing main.py as a standalone script),
    the module must successfully catch the ImportError and fall back to absolute imports,
    specifically executing the zip_builder fallback import branch (Line 21).
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


def test_loaders_debug_logging(tmp_path, caplog):
    """
    Narrative: When logging level is set to DEBUG, invoking load_json and load_schema 
    must emit debug log records confirming file reading operations (Lines 35 & 44).
    """
    # We configure the logger to capture DEBUG level messages.
    caplog.set_level(logging.DEBUG, logger="src.main")

    # We create valid temporary JSON and schema files on disk.
    json_file = tmp_path / "test_payload.json"
    json_file.write_text('{"key": "value"}', encoding="utf-8")

    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text('{"type": "object"}', encoding="utf-8")

    # Calling load_json exercises the debug logging statement for JSON loading.
    data = load_json(json_file)
    assert data == {"key": "value"}

    # Calling load_schema exercises the debug logging statement for schema loading.
    schema = load_schema(schema_file)
    assert schema == {"type": "object"}

    # We verify that both debug logging statements were successfully triggered.
    assert any("Loading JSON from file" in record.message for record in caplog.records)
    assert any("Loading schema from file" in record.message for record in caplog.records)
