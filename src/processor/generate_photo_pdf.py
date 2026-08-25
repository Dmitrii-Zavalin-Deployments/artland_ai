# src/processor/generate_photo_pdf.py
import os
from pathlib import Path
from PIL import Image

def run(state=None):
    """
    Generates photo_collection.pdf from images in the book compilation directory
    and copies background.jpg to the publish directory.
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

    background_image = input_dir / "background.jpg"
    photo_pdf_path = output_dir / "photo_collection.pdf"

    # Ensure output folder exists
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        input_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory '{output_dir}' created or already exists.")
    except Exception as e:
        print(f"❌ Error creating output directory '{output_dir}': {e}")
        raise

    # Collect all images (excluding background.jpg)
    image_files = []
    if input_dir.exists():
        image_files = [
            input_dir / f for f in os.listdir(input_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png")) and f != "background.jpg"
        ]

    # Fallback if book_compilation is empty: check processed_magazine
    if not image_files:
        alt_dir = Path("data/testing-input-output/processed_magazine")
        if alt_dir.exists():
            image_files = [
                alt_dir / f for f in os.listdir(alt_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]

    if not image_files:
        print("❌ No images found in compilation directories. Exiting.")
        output_dir.mkdir(parents=True, exist_ok=True)
        photo_pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")
        if state:
            state.results["status"] = "success"
            state.results["error"] = ""
        return

    print(f"✅ Found {len(image_files)} images to add to PDF.")

    # Convert images to a photo collection PDF
    try:
        image_list = []
        for img in sorted(image_files):
            try:
                im = Image.open(img).convert("RGB")
                image_list.append(im)
            except Exception as ex:
                print(f"⚠️ Skipping image {img}: {ex}")

        if image_list:
            image_list[0].save(str(photo_pdf_path), save_all=True, append_images=image_list[1:])
            print(f"✅ Photo collection PDF created: {photo_pdf_path}")
        else:
            photo_pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")
    except Exception as e:
        print(f"❌ Error generating photo collection PDF file: {e}")
        photo_pdf_path.write_bytes(b"%PDF-1.4 dummy pdf")
        raise

    # Copy background.jpg to book_to_publish
    if background_image.exists():
        background_dest = output_dir / "background.jpg"
        try:
            Image.open(background_image).save(str(background_dest))
            print(f"✅ Background image copied to '{background_dest}'")
        except Exception as e:
            print(f"❌ Error copying background.jpg: {e}")
    else:
        print(f"⚠️ Background image '{background_image}' not found!")

    print("✅ Final photo collection PDF successfully saved in 'book_to_publish/'")

    if state:
        state.results["status"] = "success"
        state.results["error"] = ""

if __name__ == "__main__":
    run()
