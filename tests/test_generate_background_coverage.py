# tests/test_generate_background_coverage.py
import cv2
import numpy as np
import pytest

import processor.generate_background as gb
from state import State


def test_extract_colors_file_not_found(tmp_path):
    """Covers line 19: FileNotFoundError when image path does not exist."""
    missing = tmp_path / "missing.jpg"
    with pytest.raises(FileNotFoundError, match="Image not found"):
        gb.extract_colors_from_image(missing, num_colors=3, brightness_threshold=100)


def test_extract_colors_invalid_image(tmp_path):
    """Covers line 25: ValueError when OpenCV fails to read image."""
    corrupt = tmp_path / "corrupt.jpg"
    corrupt.write_bytes(b"not an image")
    with pytest.raises(ValueError, match="Failed to read image"):
        gb.extract_colors_from_image(corrupt, num_colors=3, brightness_threshold=100)


def test_process_images_folder_not_found(tmp_path):
    """Covers line 51: FileNotFoundError when image folder does not exist."""
    missing_folder = tmp_path / "no_folder"
    with pytest.raises(FileNotFoundError, match="Image folder not found"):
        gb.process_images(missing_folder, num_colors=3, brightness_threshold=100)


def test_process_images_no_images_found(tmp_path):
    """Covers line 57: FileNotFoundError when folder has no jpg/png files."""
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()
    with pytest.raises(FileNotFoundError, match="No image files"):
        gb.process_images(empty_folder, num_colors=3, brightness_threshold=100)


def test_group_colors_empty():
    """Covers line 73: return colors when colors list is empty."""
    assert gb.group_colors_by_lightness([]) == []


def test_create_smoother_gradient_single_color():
    """Covers line 86: len(colors_sorted) < 2 duplicates colors."""
    single_color = [[200, 200, 200]]
    result = gb.create_smoother_gradient_background(single_color, width=10, height=10)
    assert result.shape == (10, 10, 3)


def test_create_smoother_gradient_index_bound(monkeypatch):
    """Covers line 93: primary_color_index >= len(colors_sorted) - 1 boundary condition."""
    colors = [[255, 255, 255], [0, 0, 0]]
    # Monkeypatch range in generate_background module to trigger boundary index condition
    monkeypatch.setattr("builtins.range", lambda x: [0, int(x)])
    result = gb.create_smoother_gradient_background(colors, width=10, height=2)
    assert result.shape == (2, 10, 3)


def test_run_missing_state():
    """Covers line 126 & lines 175-177: ValueError wrapped in RuntimeError when state is None."""
    with pytest.raises(RuntimeError, match="Error generating background"):
        gb.run(None)


def test_run_missing_book_compilation_dir(tmp_path):
    """Covers line 129 & lines 175-177: AttributeError wrapped in RuntimeError when book_compilation_dir missing."""
    state = State({}, {}, tmp_path)
    if hasattr(state, "book_compilation_dir"):
        delattr(state, "book_compilation_dir")
    with pytest.raises(RuntimeError, match="Error generating background"):
        gb.run(state)


def test_run_invalid_config(tmp_path):
    """Covers line 135 & lines 175-177: KeyError wrapped when state.config is not a dict."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.config = "not_a_dict"
    with pytest.raises(RuntimeError, match="Error generating background"):
        gb.run(state)


def test_run_missing_generate_background_config(tmp_path):
    """Covers line 139 & lines 175-177: KeyError wrapped when generate_background config block is missing."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.config = {"other": {}}
    with pytest.raises(RuntimeError, match="Error generating background"):
        gb.run(state)


def test_run_missing_config_fields(tmp_path):
    """Covers line 156 & lines 175-177: ValueError wrapped when required config fields are missing."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.config = {
        "generate_background": {
            "brightness_threshold": 100
            # missing other required fields
        }
    }
    with pytest.raises(RuntimeError, match="Error generating background"):
        gb.run(state)


def test_run_fallback_colors_and_success(tmp_path):
    """Covers lines 166-167 (fallback colors when no colors extracted) and successful generation/saving."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a dark image in the folder so process_images finds it but extracts 0 bright colors
    img_path = state.book_compilation_dir / "sample.jpg"
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)

    state.config = {
        "generate_background": {
            "brightness_threshold": 250,  # High threshold triggers fallback colors
            "num_colors_per_image": 3,
            "gradient_width": 100,
            "gradient_height": 100,
            "fallback_colors": [[255, 255, 255], [100, 100, 100], [0, 0, 0]]
        }
    }

    gb.run(state)

    output_file = state.book_compilation_dir / "cover_background.jpg"
    assert output_file.exists()
