# tests/test_artistic_painting_processor_coverage.py
import cv2
import numpy as np
import pytest

import processor.artistic_painting_processor as app
from state import State


def test_refined_transformation_file_not_found(tmp_path):
    """Covers line 21: FileNotFoundError when input image path does not exist."""
    missing_image = tmp_path / "non_existent.jpg"
    output_image = tmp_path / "output.jpg"
    config = {}

    with pytest.raises(FileNotFoundError, match="Input image for artistic transformation not found"):
        app.refined_artistic_transformation(missing_image, output_image, config)


def test_refined_transformation_invalid_config_type(tmp_path):
    """Covers line 27: TypeError when config is not a valid dictionary."""
    valid_image = tmp_path / "valid.jpg"
    cv2.imwrite(str(valid_image), np.zeros((50, 50, 3), dtype=np.uint8))
    output_image = tmp_path / "output.jpg"

    with pytest.raises(TypeError, match="'config' must be a valid dictionary"):
        app.refined_artistic_transformation(valid_image, output_image, config="not_a_dict")


def test_refined_transformation_missing_config_fields(tmp_path):
    """Covers line 57: ValueError when required config keys are missing."""
    valid_image = tmp_path / "valid.jpg"
    cv2.imwrite(str(valid_image), np.zeros((50, 50, 3), dtype=np.uint8))
    output_image = tmp_path / "output.jpg"

    # Incomplete configuration missing required keys
    incomplete_config = {
        "bilateral_d": 9
        # Missing all other 12 required keys
    }

    with pytest.raises(ValueError, match="Required 'artistic_painting' config fields missing"):
        app.refined_artistic_transformation(valid_image, output_image, incomplete_config)


def test_run_missing_state():
    """Covers line 123 & lines 140-142: ValueError wrapped in RuntimeError when state is None."""
    with pytest.raises(RuntimeError, match="Error processing the image"):
        app.run(None)


def test_run_missing_current_frame_path(tmp_path):
    """Covers line 126 & lines 140-142: AttributeError wrapped in RuntimeError when state lacks current_frame_path."""
    state = State({}, {}, tmp_path)
    state.current_frame_path = None

    with pytest.raises(RuntimeError, match="Error processing the image"):
        app.run(state)


def test_run_invalid_config_dictionary(tmp_path):
    """Covers line 131 & lines 140-142: KeyError wrapped in RuntimeError when state.config is not a dict."""
    valid_image = tmp_path / "valid.jpg"
    cv2.imwrite(str(valid_image), np.zeros((50, 50, 3), dtype=np.uint8))

    state = State({}, {}, tmp_path)
    state.current_frame_path = valid_image
    state.config = "invalid_config_not_a_dict"

    with pytest.raises(RuntimeError, match="Error processing the image"):
        app.run(state)


def test_run_missing_artistic_painting_block(tmp_path):
    """Covers line 135 & lines 140-142: KeyError wrapped in RuntimeError when 'artistic_painting' is missing from config."""
    valid_image = tmp_path / "valid.jpg"
    cv2.imwrite(str(valid_image), np.zeros((50, 50, 3), dtype=np.uint8))

    state = State({}, {}, tmp_path)
    state.current_frame_path = valid_image
    state.config = {"some_other_key": {}}

    with pytest.raises(RuntimeError, match="Error processing the image"):
        app.run(state)


def test_successful_run_and_transformation(tmp_path):
    """Covers successful execution of both refined_artistic_transformation and run()."""
    valid_image = tmp_path / "valid.jpg"
    # Create a small random color image so skimage/cv2 processors run through all steps successfully
    img_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(valid_image), img_data)

    complete_config = {
        "artistic_painting": {
            "bilateral_d": 9,
            "sigma_color": 75,
            "sigma_space": 75,
            "canny_threshold1": 100,
            "canny_threshold2": 200,
            "depth_alpha": 1.2,
            "depth_beta": 10,
            "saturation_multiplier": 1.3,
            "brightness_multiplier": 1.1,
            "stylization_sigma_s": 60,
            "stylization_sigma_r": 0.45,
            "detail_sigma_s": 10,
            "detail_sigma_r": 0.15
        }
    }

    state = State({}, complete_config, tmp_path)
    state.current_frame_path = valid_image

    # Execute run function successfully
    app.run(state)
    assert valid_image.exists()
