# tests/test_add_fading_edges_coverage.py
import cv2
import numpy as np
import pytest

import processor.add_fading_edges as afte
from state import State


def test_apply_proportional_whitening_file_not_found(tmp_path):
    """Covers line 19: FileNotFoundError when input image does not exist."""
    non_existent = tmp_path / "missing.jpg"
    with pytest.raises(FileNotFoundError, match="Input image for fading edges not found"):
        afte.apply_proportional_whitening(non_existent, {"canvas_width": 200, "canvas_height": 200, "top_bottom_divisor": 4, "left_right_divisor": 4})


def test_apply_proportional_whitening_invalid_image(tmp_path):
    """Covers line 26: ValueError when OpenCV fails to load the image (image is None)."""
    bad_file = tmp_path / "corrupt.jpg"
    bad_file.write_bytes(b"not an image file")

    with pytest.raises(ValueError, match="Failed to load image from.*via OpenCV"):
        afte.apply_proportional_whitening(bad_file, {"canvas_width": 200, "canvas_height": 200, "top_bottom_divisor": 4, "left_right_divisor": 4})


def test_apply_proportional_whitening_invalid_config_type(tmp_path):
    """Covers line 32: TypeError when config is not a dictionary."""
    valid_img = tmp_path / "valid.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(valid_img), img)

    with pytest.raises(TypeError, match="'config' must be a valid dictionary"):
        afte.apply_proportional_whitening(valid_img, config="not_a_dict")


def test_apply_proportional_whitening_missing_config_fields(tmp_path):
    """Covers line 48: ValueError when required config fields are missing."""
    valid_img = tmp_path / "valid.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(valid_img), img)

    # Missing left_right_divisor and canvas_height
    incomplete_config = {
        "canvas_width": 200,
        "top_bottom_divisor": 4
    }

    with pytest.raises(ValueError, match="Required 'fading_edges' config fields missing"):
        afte.apply_proportional_whitening(valid_img, config=incomplete_config)


def test_run_missing_state(tmp_path):
    """Covers line 113: ValueError when state is None or missing in run()."""
    with pytest.raises(RuntimeError, match="Error processing fading edges"):
        afte.run(None)


def test_run_missing_current_frame_path(tmp_path):
    """Covers line 116: AttributeError when state lacks current_frame_path."""
    state = State({}, {}, tmp_path)
    state.current_frame_path = None

    with pytest.raises(RuntimeError, match="Error processing fading edges"):
        afte.run(state)


def test_run_missing_or_invalid_config_dict(tmp_path):
    """Covers line 121: KeyError when state.config is missing or not a dictionary."""
    state = State({}, {}, tmp_path)
    state.current_frame_path = tmp_path / "sample.jpg"
    state.config = "invalid_config"

    with pytest.raises(RuntimeError, match="Error processing fading edges"):
        afte.run(state)


def test_run_missing_fading_edges_block(tmp_path):
    """Covers line 125: KeyError when 'fading_edges' key is missing from config."""
    state = State({}, {}, tmp_path)
    state.current_frame_path = tmp_path / "sample.jpg"
    state.config = {"other_section": {}}

    with pytest.raises(RuntimeError, match="Error processing fading edges"):
        afte.run(state)


def test_run_successful_execution_and_exception_handling(tmp_path):
    """Covers successful run and lines 130-132 (global exception handler/logging/RuntimeError wrap)."""
    valid_img = tmp_path / "sample.jpg"
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(valid_img), img)

    config_data = {
        "fading_edges": {
            "canvas_width": 200,
            "canvas_height": 200,
            "top_bottom_divisor": 4,
            "left_right_divisor": 4
        }
    }

    state = State({}, config_data, tmp_path)
    state.current_frame_path = valid_img

    # Test successful execution
    afte.run(state)
    assert valid_img.exists()

    # Test exception handler & wrapping (lines 130-132) by passing invalid image path that triggers inner exception
    state.current_frame_path = tmp_path / "does_not_exist.jpg"
    with pytest.raises(RuntimeError, match="Error processing fading edges"):
        afte.run(state)
