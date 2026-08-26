# tests/test_state_coverage.py
from pathlib import Path
import pytest

from state import State


def test_state_inputs_not_dict(tmp_path):
    """Covers line 14: TypeError when inputs is not a valid dictionary."""
    with pytest.raises(TypeError, match="'inputs' must be a valid dictionary"):
        State(inputs="not_a_dict", config={}, input_output_folder=tmp_path)


def test_state_config_not_dict(tmp_path):
    """Covers line 16: TypeError when config is not a valid dictionary."""
    with pytest.raises(TypeError, match="'config' must be a valid dictionary"):
        State(inputs={}, config="not_a_dict", input_output_folder=tmp_path)


def test_state_folder_missing():
    """Covers line 18: ValueError when input_output_folder is missing or empty."""
    with pytest.raises(ValueError, match="'input_output_folder' is missing or empty"):
        State(inputs={}, config={}, input_output_folder="")


def test_write_output_json_missing_datetime(tmp_path):
    """Covers line 51: populates date_time in results if missing when writing JSON."""
    state = State({}, {}, tmp_path)
    # Remove date_time to trigger line 51
    state.results.pop("date_time", None)

    output_path = tmp_path / "output.json"
    state.write_output_json(output_path)

    assert output_path.exists()
    assert "date_time" in state.results


def test_write_output_json_exception(tmp_path, monkeypatch):
    """Covers lines 63-65: RuntimeError wrapped around exception during JSON writing."""
    state = State({}, {}, tmp_path)
    output_path = tmp_path / "output.json"

    # Simulate an OSError during file open/write
    def mock_open(*args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    with pytest.raises(RuntimeError, match="Could not write output JSON"):
        state.write_output_json(output_path)
