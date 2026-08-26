# tests/test_expand_image_coverage.py
from pathlib import Path
import pytest
from PIL import Image

import processor.expand_image as ei
from state import State


def test_expand_background_image_file_not_found(tmp_path):
    """Covers line 19: FileNotFoundError when the target image doesn't exist."""
    missing_image = tmp_path / "non_existent.jpg"
    with pytest.raises(FileNotFoundError, match="Background image not found"):
        ei.expand_background_image(missing_image, scale_factor_y=2, num_repeats_x=2)


def test_run_missing_state():
    """Covers line 52 & lines 94-96: ValueError wrapped in RuntimeError when state is None."""
    with pytest.raises(RuntimeError, match="Error expanding image"):
        ei.run(None)


def test_run_missing_book_compilation_dir(tmp_path):
    """Covers line 55 & lines 94-96: AttributeError wrapped in RuntimeError when book_compilation_dir is missing."""
    state = State({}, {}, tmp_path)
    if hasattr(state, "book_compilation_dir"):
        delattr(state, "book_compilation_dir")

    with pytest.raises(RuntimeError, match="Error expanding image"):
        ei.run(state)


def test_run_both_images_missing(tmp_path):
    """Covers lines 64-65 & lines 94-96: FileNotFoundError wrapped when neither cover nor alt image exists."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    
    # Do NOT create any images
    with pytest.raises(RuntimeError, match="Error expanding image"):
        ei.run(state)


def test_run_invalid_config_type(tmp_path):
    """Covers line 70 & lines 94-96: KeyError wrapped when state.config is not a dictionary."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    
    # Create cover_background to bypass file check
    (state.book_compilation_dir / "cover_background.jpg").touch()
    
    state.config = "invalid_config_type"
    with pytest.raises(RuntimeError, match="Error expanding image"):
        ei.run(state)


def test_run_missing_expand_image_block(tmp_path):
    """Covers line 74 & lines 94-96: KeyError wrapped when 'expand_image' is missing in config."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    (state.book_compilation_dir / "cover_background.jpg").touch()
    
    state.config = {"some_other_key": {}}
    with pytest.raises(RuntimeError, match="Error expanding image"):
        ei.run(state)


def test_run_missing_config_fields(tmp_path):
    """Covers line 86 & lines 94-96: ValueError wrapped when specific config values are missing."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    (state.book_compilation_dir / "cover_background.jpg").touch()
    
    state.config = {
        "expand_image": {
            "scale_factor_y": 2
            # Missing num_repeats_x
        }
    }
    with pytest.raises(RuntimeError, match="Error expanding image"):
        ei.run(state)


def test_run_alt_path_exists_and_successful_run(tmp_path):
    """Covers lines 62-63 (fallback to alt_path) and standard successful execution."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    
    # Intentionally do not create "cover_background.jpg", only "background.jpg"
    alt_path = state.book_compilation_dir / "background.jpg"
    
    # Create a small valid image to be processed successfully by PIL
    img = Image.new("RGB", (10, 20), color="blue")
    img.save(alt_path)

    state.config = {
        "expand_image": {
            "scale_factor_y": 2,
            "num_repeats_x": 3
        }
    }

    ei.run(state)

    # Check if the fallback alt image was properly loaded, resized, repeated, and overwritten
    with Image.open(alt_path) as result:
        assert result.size == (30, 40)  # Width: 10*3 = 30, Height: 20*2 = 40


def test_run_primary_image_successful(tmp_path):
    """Covers the default successful flow when cover_background.jpg exists."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = tmp_path / "book"
    state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
    
    # Create primary image "cover_background.jpg"
    primary_path = state.book_compilation_dir / "cover_background.jpg"
    img = Image.new("RGB", (5, 5), color="red")
    img.save(primary_path)

    state.config = {
        "expand_image": {
            "scale_factor_y": 4,
            "num_repeats_x": 5
        }
    }

    ei.run(state)

    with Image.open(primary_path) as result:
        assert result.size == (25, 20)  # Width: 5*5 = 25, Height: 5*4 = 20
