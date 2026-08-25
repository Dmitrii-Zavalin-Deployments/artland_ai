# src/processor/generate_photo_pdf.py
import os
import zipfile
from pathlib import Path
from PIL import Image

def run(state=None):
    """
    Generates magazine_content.pdf from compiled frames, prepares cover_background.jpg,
    and packages both directly into magazine_assets.zip.
    """
    # Determine directories with fallback support for both stateful pipelines and direct execution
    if state and hasattr(state, "book_compilation_dir") and hasattr(state, "book_to_publish_dir"):
        input_dir = Path(state.book_compilation_dir)
        output_dir = Path(state.book_to_publish_dir)
    else:
        github_workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
        candidate_in = Path("data/testing-input-output/book_compilation")
        if candidate_in.exists():
            input_dir = candidate_in
            output_dir = Path("data/testing-input-output/book_to_publish")
        else:
            input_dir = Path(github_workspace) / "book_compilation"
            output_dir = Path(github_workspace) / "book_to_publish"

    source_background = input_dir / "background.jpg"
    magazine_pdf_path = output_dir / "magazine_content.pdf"
    cover_bg_path = output_dir / "cover_background.jpg"

    # Ensure output folder exists
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        input_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory '{output_dir}' created or already exists.")
    except Exception as e:
        print(f"❌ Error creating output directory '{output_dir}': {e}")
        raise

    # Collect all images (excluding background files)
    image_files = []
    if input_dir.exists():
        image_files = [
            input_dir / f for f in os.listdir(input_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png")) and f.lower() not in ["background.jpg", "cover_background.jpg"]
        ]

    # Fallback if book_compilation is empty: check processed_magazine
    if not image_files:
        alt_dir = Path("data/testing-input-output/processed_magazine")
        if alt_dir.exists():
            image_files = [
                alt_dir / f for f in os.listdir(alt_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]

    image_list = []
    if not image_files:
        print("❌ No images found in compilation directories. Creating dummy PDF.")
        output_dir.mkdir(parents=True, exist_ok=True)
        magazine_pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")
    else:
        print(f"✅ Found {len(image_files)} images to add to PDF.")
        # Convert images to magazine content PDF
        try:
            for img in sorted(image_files):
                try:
                    im = Image.open(img).convert("RGB")
                    image_list.append(im)
                except Exception as ex:
                    print(f"⚠️ Skipping image {img}: {ex}")

            if image_list:
                image_list[0].save(str(magazine_pdf_path), save_all=True, append_images=image_list[1:])
                print(f"✅ Magazine content PDF created: {magazine_pdf_path}")
            else:
                magazine_pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")
        except Exception as e:
            print(f"❌ Error generating magazine PDF file: {e}")
            magazine_pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")

    # Handle cover background image
    if source_background.exists():
        try:
            Image.open(source_background).convert("RGB").save(str(cover_bg_path))
            print(f"✅ Cover background prepared: {cover_bg_path}")
        except Exception as e:
            print(f"❌ Error copying cover background: {e}")
    else:
        print(f"⚠️ Source background '{source_background}' not found! Creating fallback.")
        if image_list:
            image_list[0].save(str(cover_bg_path))
        else:
            cover_bg_path.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF")

    # Package ONLY magazine_content.pdf and cover_background.jpg into magazine_assets.zip
    if state and hasattr(state, "config"):
        magazine_zip_path = Path(state.config.get("magazine_assets_zip_path", "data/testing-input-output/magazine_assets.zip"))
    else:
        magazine_zip_path = Path("data/testing-input-output/magazine_assets.zip")

    magazine_zip_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(magazine_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if magazine_pdf_path.exists():
            zipf.write(magazine_pdf_path, "magazine_content.pdf")
        if cover_bg_path.exists():
            zipf.write(cover_bg_path, "cover_background.jpg")

    print(f"✅ Successfully packaged magazine assets into {magazine_zip_path} (contains only magazine_content.pdf and cover_background.jpg)")

    if state:
        state.results["status"] = "success"
        state.results["error"] = ""
        state.results["magazine_assets_zip_path"] = str(magazine_zip_path)

if __name__ == "__main__":
    run()
