import json
import logging
import sys
import zipfile
from pathlib import Path
from PIL import Image
import pytest

from main import main


def create_sample_image_zip(zip_path: Path):
    """Generates a valid test JPEG image and packages it into a ZIP archive."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    temp_img_path = zip_path.parent / "sample_frame.jpg"
    
    # Create a 100x100 RGB test image
    img = Image.new("RGB", (100, 100), color=(120, 150, 180))
    img.save(temp_img_path, format="JPEG")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(temp_img_path, arcname="sample_frame.jpg")

    temp_img_path.unlink()


def test_pipeline_successful_execution_path(setup_pipeline_environment, tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)

    # Prepare I/O Directory
    io_folder = tmp_path / "data" / "testing-input-output"
    io_folder.mkdir(parents=True, exist_ok=True)

    input_zip_path = io_folder / "input_frames.zip"
    processed_photos_zip_path = io_folder / "processed_photos.zip"
    magazine_assets_zip_path = io_folder / "magazine_assets.zip"

    create_sample_image_zip(input_zip_path)

    input_data = {
        "input_zip_path": str(input_zip_path),
        "processed_photos_zip_path": str(processed_photos_zip_path),
        "magazine_assets_zip_path": str(magazine_assets_zip_path),
        "title": "Artland Magazine",
        "issue": "Issue #1",
        "tagline": "Creative Visuals",
        "subtitle": "Special Edition",
        "author": "Pipeline Tester"
    }
    
    input_file_name = "input.json"
    output_file_name = "output.json"
    (io_folder / input_file_name).write_text(json.dumps(input_data, indent=2), encoding="utf-8")

    # Simulate command-line arguments passed to main.py
    cli_args = [
        "main.py",
        "--input_output_folder", str(io_folder),
        "--input_file_name", input_file_name,
        "--output_file_name", output_file_name
    ]
    monkeypatch.setattr(sys, "argv", cli_args)

    # Direct execution of main pipeline without subprocess or mocks
    main()

    # ---------------------------------------------------------
    # Assertions: Output State File & Created Archives
    # ---------------------------------------------------------
    output_json_path = io_folder / output_file_name
    assert output_json_path.exists(), "Output JSON file was not generated."

    with open(output_json_path, "r", encoding="utf-8") as f:
        output_data = json.load(f)

    assert output_data["results"]["status"] == "success"
    assert output_data["results"]["error"] == ""

    assert processed_photos_zip_path.exists(), "Video photos ZIP archive missing."
    assert magazine_assets_zip_path.exists(), "Magazine assets ZIP archive missing."

    # Validate Magazine Assets ZIP content
    with zipfile.ZipFile(magazine_assets_zip_path, "r") as zf:
        archived_files = zf.namelist()
        assert "magazine_content.pdf" in archived_files
        assert "cover_background.jpg" in archived_files
        assert "magazine_cover.html" in archived_files

    # ---------------------------------------------------------
    # Assertions: Logging across all pipeline components
    # ---------------------------------------------------------
    log_text = caplog.text

    # Main / State
    assert "Initializing main pipeline runner with folder:" in log_text
    assert "Initializing State management instance." in log_text
    assert "Writing output JSON to path:" in log_text

    # Frames Loader
    assert "Starting frames loader pipeline execution." in log_text
    assert "Discovered 1 valid image frame(s) in input ZIP." in log_text

    # Video Pipeline
    assert "Starting artistic pipeline video execution." in log_text

    # Magazine Pipeline
    assert "Starting artistic pipeline magazine execution." in log_text

    # Processors
    assert "Starting artistic_painting_processor execution." in log_text
    assert "Starting add_fading_edges execution." in log_text
    assert "Starting generate_background execution." in log_text
    assert "Starting expand_image execution." in log_text
    assert "Starting generate_photo_pdf execution." in log_text
    assert "Starting generate_cover execution." in log_text

    # Zip Builder
    assert "Starting zip_builder execution." in log_text
    assert "Zip builder execution completed successfully." in log_text
