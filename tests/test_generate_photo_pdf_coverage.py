# tests/test_generate_photo_pdf_coverage.py
import builtins
from pathlib import Path

import pytest
from PIL import Image

import processor.generate_photo_pdf as gpp
from state import State


def test_run_alternative_background(tmp_path):
    """Covers line 34: uses alt_background (background.jpg) when cover_background.jpg is missing."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()

    # Create a valid image for compilation
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50), color="red").save(img_path)

    # Create alt_background instead of cover_background.jpg
    alt_bg = input_dir / "background.jpg"
    Image.new("RGB", (50, 50), color="blue").save(alt_bg)

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)

    gpp.run(state)

    assert (output_dir / "magazine_content.pdf").exists()
    assert (output_dir / "cover_background.jpg").exists()


def test_run_input_dir_not_exists(tmp_path):
    """Covers line 42: FileNotFoundError when compilation input directory does not exist."""
    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(tmp_path / "nonexistent_compilation")
    state.book_to_publish_dir = str(tmp_path / "publish")

    with pytest.raises(FileNotFoundError, match="Compiling input directory does not exist"):
        gpp.run(state)


def test_run_no_valid_images_found(tmp_path):
    """Covers line 53: FileNotFoundError when no valid compilation images are found."""
    input_dir = tmp_path / "compilation"
    input_dir.mkdir()
    # Only background exists, no content images
    (input_dir / "cover_background.jpg").touch()

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(tmp_path / "publish")

    with pytest.raises(FileNotFoundError, match="No valid magazine compilation images found"):
        gpp.run(state)


def test_run_empty_image_list_value_error(tmp_path):
    """Covers FileNotFoundError when no valid compilation images are found."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()
    (input_dir / "cover_background.jpg").touch()

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)

    with pytest.raises(FileNotFoundError, match="No valid magazine compilation images found"):
        gpp.run(state)


def _mock_empty_image():
    class Dummy:
        def convert(self, mode):
            return self
    # To test line 69 specifically, if image_list is empty:
    # Let's mock a scenario where image_list is empty after loop or before save.


def test_run_pdf_generation_exception(tmp_path, monkeypatch):
    """Covers lines 73-75: RuntimeError when an exception occurs during PDF generation."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50)).save(img_path)
    (input_dir / "cover_background.jpg").touch()

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)

    # Force an exception during image processing/saving
    def mock_open_raise(p):
        raise OSError("Disk read error")

    monkeypatch.setattr(Image, "open", mock_open_raise)

    with pytest.raises(RuntimeError, match="Error generating magazine PDF file"):
        gpp.run(state)


def test_run_source_background_missing(tmp_path):
    """Covers line 79: FileNotFoundError when neither cover_background.jpg nor background.jpg exists."""
    input_dir = tmp_path / "compilation"
    input_dir.mkdir()
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50)).save(img_path)
    # No background files present

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(tmp_path / "publish")

    with pytest.raises(FileNotFoundError, match="Source background image not found"):
        gpp.run(state)


def test_run_cover_background_processing_exception(tmp_path, monkeypatch):
    """Covers lines 87-89: RuntimeError when processing cover background fails."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50)).save(img_path)
    bg_path = input_dir / "cover_background.jpg"
    Image.new("RGB", (50, 50)).save(bg_path)

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)

    original_open = Image.open
    def mock_open(path, *args, **kwargs):
        if Path(path) == bg_path:
            raise RuntimeError("Background corruption")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Image, "open", mock_open)

    with pytest.raises(RuntimeError, match="Error processing cover background"):
        gpp.run(state)


def test_run_custom_magazine_assets_zip_path(tmp_path):
    """Covers line 96: custom magazine_assets_zip_path from state.config."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50)).save(img_path)
    bg_path = input_dir / "cover_background.jpg"
    Image.new("RGB", (50, 50)).save(bg_path)

    custom_zip = tmp_path / "custom_folder" / "custom_assets.zip"

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)
    state.config = {"magazine_assets_zip_path": str(custom_zip)}

    gpp.run(state)

    assert custom_zip.exists()


def test_run_state_results_is_none(tmp_path):
    """Covers line 114: initializes state.results = {} when state.results is None."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50)).save(img_path)
    bg_path = input_dir / "cover_background.jpg"
    Image.new("RGB", (50, 50)).save(bg_path)

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)
    state.results = None

    gpp.run(state)

    assert state.results is not None
    assert state.results["status"] == "success"


def test_production_runtime_state_with_and_without_config(monkeypatch):
    """Covers lines 122-130: ProductionRuntimeState initialization with and without config.json."""
    # Test when config.json exists
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr("json.load", lambda f: {"test": "config"})
    runtime_state_exists = gpp.ProductionRuntimeState()
    assert runtime_state_exists.config == {"test": "config"}

    # Test when config.json does not exist
    monkeypatch.setattr(Path, "exists", lambda self: "config.json" not in str(self))
    runtime_state_missing = gpp.ProductionRuntimeState()
    assert runtime_state_missing.config == {}


def test_main_execution(monkeypatch):
    """Covers lines 134-135: main() execution function."""
    monkeypatch.setattr(gpp, "run", lambda state: None)
    gpp.main()

def test_run_image_list_empty_value_error(tmp_path, monkeypatch):
    """Covers line 69: ValueError when image_list is empty during PDF generation."""
    input_dir = tmp_path / "compilation"
    output_dir = tmp_path / "publish"
    input_dir.mkdir()
    
    # Create valid dummy files so line 52 (image_files check) passes
    img_path = input_dir / "frame1.jpg"
    Image.new("RGB", (50, 50)).save(img_path)
    bg_path = input_dir / "cover_background.jpg"
    Image.new("RGB", (50, 50)).save(bg_path)

    state = State({}, {}, tmp_path)
    state.book_compilation_dir = str(input_dir)
    state.book_to_publish_dir = str(output_dir)

    # Monkeypatch builtins.sorted to return an empty list for our image files,
    # causing the compilation loop to be skipped and image_list to remain empty.
    orig_sorted = builtins.sorted
    def mock_sorted(iterable, *args, **kwargs):
        if any(str(img_path) in str(x) for x in iterable):
            return []
        return orig_sorted(iterable, *args, **kwargs)

    monkeypatch.setattr(builtins, "sorted", mock_sorted)

    with pytest.raises(RuntimeError, match="Error generating magazine PDF file"):
        gpp.run(state)