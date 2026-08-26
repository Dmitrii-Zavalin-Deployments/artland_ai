# tests/test_frames_loader_coverage.py
import zipfile

import pytest

import frames_loader
from state import State


def test_frames_loader_missing_inputs_key(setup_pipeline_environment, tmp_path):
    """Covers line 19: KeyError when input_zip_path is missing or inputs dict is empty/absent."""
    # Case 1: Missing inputs attribute or empty dictionary
    state1 = State({}, {}, tmp_path)
    with pytest.raises(KeyError, match="Required key 'input_zip_path' is missing"):
        frames_loader.run(state1)

    # Case 2: Inputs dict provided but lacks 'input_zip_path'
    state2 = State({}, {}, tmp_path)
    state2.inputs = {"wrong_key": "some_value"}
    with pytest.raises(KeyError, match="Required key 'input_zip_path' is missing"):
        frames_loader.run(state2)


def test_frames_loader_file_not_found(setup_pipeline_environment, tmp_path):
    """Covers line 23: FileNotFoundError when input ZIP path does not exist."""
    state = State({}, {}, tmp_path)
    state.inputs = {"input_zip_path": str(tmp_path / "non_existent_archive.zip")}

    with pytest.raises(FileNotFoundError, match="Input ZIP file not found at"):
        frames_loader.run(state)


def test_frames_loader_no_valid_frames_raises_value_error(setup_pipeline_environment, tmp_path):
    """Covers line 44: ValueError when ZIP archive contains no supported image files (.jpg/.jpeg/.png)."""
    zip_file = tmp_path / "empty_frames.zip"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("notes.txt", "just text")
        zf.writestr("data.csv", "id,value\n1,100")

    state = State({}, {}, tmp_path)
    state.inputs = {"input_zip_path": str(zip_file)}

    with pytest.raises(ValueError, match="NO-DEFAULT POLICY VIOLATION: No valid JPG/PNG frames found"):
        frames_loader.run(state)


def test_frames_loader_successful_extraction_and_results_init(setup_pipeline_environment, tmp_path):
    """Covers lines 36-38 (recursive extraction/filtering) and line 50 (results init when None)."""
    zip_file = tmp_path / "valid_frames.zip"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("frame1.jpg", b"fake jpeg data")
        zf.writestr("subfolder/frame2.png", b"fake png data")
        zf.writestr("readme.txt", b"ignore me")

    state = State({}, {}, tmp_path)
    state.inputs = {"input_zip_path": str(zip_file)}
    state.results = None  # Force None to test line 50 initialization branch

    frames_loader.run(state)

    assert state.results["status"] == "success"
    assert state.results["error"] == ""
    assert len(state.frame_paths) == 2


def test_frames_loader_exception_handling_block(setup_pipeline_environment, tmp_path):
    """Covers lines 55-61: Global exception catch block, error state initialization, and logging."""
    zip_file = tmp_path / "corrupt.zip"
    zip_file.write_bytes(b"not a valid zip file structure")

    state = State({}, {}, tmp_path)
    state.inputs = {"input_zip_path": str(zip_file)}
    state.results = None  # Force None to test line 56-57 initialization inside exception handler

    with pytest.raises(Exception):
        frames_loader.run(state)

    assert state.results["status"] == "error"
    assert "File is not a zip file" in state.results["error"] or len(state.results["error"]) > 0
