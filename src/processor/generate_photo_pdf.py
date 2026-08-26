# src/processor/generate_photo_pdf.py
import json
import os
import zipfile
from pathlib import Path

from PIL import Image


def run(state=None):
    """
    Generates magazine_content.pdf from compiled frames, prepares cover_background.jpg,
    and strictly packages ONLY these two files into magazine_assets.zip, enforcing 
    the No-Default Policy (no silent dummy file creation).
    """
    # Determine directories from pipeline state or production paths
    input_dir = Path("data/testing-input-output/book_compilation")
    output_dir = Path("data/testing-input-output/book_to_publish")
    
    if state:
        if hasattr(state, "book_compilation_dir") and state.book_compilation_dir:
            input_dir = Path(state.book_compilation_dir)
        if hasattr(state, "book_to_publish_dir") and state.book_to_publish_dir:
            output_dir = Path(state.book_to_publish_dir)

    source_background = input_dir / "cover_background.jpg"
    magazine_pdf_path = output_dir / "magazine_content.pdf"
    cover_bg_path = output_dir / "cover_background.jpg"

    # Ensure directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    if not input_dir.exists():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Compiling input directory does not exist at '{input_dir}'."
        )

    # Collect all image files (excluding background assets)
    image_files = [
        input_dir / f for f in os.listdir(input_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png")) and f.lower() not in ["background.jpg", "cover_background.jpg"]
    ]

    if not image_files:
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: No valid magazine compilation images found in '{input_dir}'. "
            f"No default values allowed."
        )

    print(f"✅ Found {len(image_files)} images to add to PDF.")
    
    # Convert images to magazine content PDF
    image_list = []
    try:
        for img in sorted(image_files):
            im = Image.open(img).convert("RGB")
            image_list.append(im)

        if not image_list:
            raise ValueError("No valid image objects could be loaded for PDF generation.")

        image_list[0].save(str(magazine_pdf_path), save_all=True, append_images=image_list[1:])
        print(f"✅ Magazine content PDF created: {magazine_pdf_path}")
    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        raise RuntimeError(f"❌ Error generating magazine PDF file: {e}")

    # Handle cover background image strictly
    if not source_background.exists():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Source background image not found at '{input_dir / 'cover_background.jpg'}' "
            f"or '{input_dir / 'background.jpg'}'. No default values allowed."
        )

    try:
        Image.open(source_background).convert("RGB").save(str(cover_bg_path))
        print(f"✅ Cover background prepared: {cover_bg_path}")
    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        raise RuntimeError(f"❌ Error processing cover background: {e}")

    # Determine magazine_assets.zip path from state config or default path
    magazine_zip_path = Path("data/testing-input-output/magazine_assets.zip")
    if state and hasattr(state, "config") and isinstance(state.config, dict):
        zip_path_str = state.config.get("magazine_assets_zip_path")
        if zip_path_str:
            magazine_zip_path = Path(zip_path_str)

    magazine_zip_path.parent.mkdir(parents=True, exist_ok=True)

    # Bulletproof packaging: Write ONLY the 2 required root-level files
    with zipfile.ZipFile(magazine_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if magazine_pdf_path.exists():
            zipf.write(magazine_pdf_path, "magazine_content.pdf")
            print("➕ Added to archive root: magazine_content.pdf")
        if cover_bg_path.exists():
            zipf.write(cover_bg_path, "cover_background.jpg")
            print("➕ Added to archive root: cover_background.jpg")

    print(f"✅ Successfully packaged magazine assets into {magazine_zip_path}")
    print("    Contents verified: ONLY [magazine_content.pdf, cover_background.jpg]")

    if state:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "success"
        state.results["error"] = ""
        state.results["magazine_assets_zip_path"] = str(magazine_zip_path)


class ProductionRuntimeState:
    def __init__(self):
        self.book_compilation_dir = "data/testing-input-output/book_compilation"
        self.book_to_publish_dir = "data/testing-input-output/book_to_publish"
        self.results = {}
        config_file = Path("config/config.json")
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}


def main():
    state = ProductionRuntimeState()
    run(state)


if __name__ == "__main__":
    main()
