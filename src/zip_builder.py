# src/zip_builder.py
import zipfile
from pathlib import Path


def zip_directory(source_dir: Path, zip_path: Path):
    """Utility: zip all files inside a directory under strict No-Default checks."""
    source_dir = Path(source_dir)
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Source directory for video photos not found at '{source_dir}'."
        )
    
    files = [p for p in source_dir.glob("**/*") if p.is_file()]
    if not files:
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Source directory '{source_dir}' is empty. "
            f"No processed photos found to zip. Real image processing pipeline output is required."
        )
        
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(files):
            arcname = file_path.relative_to(source_dir)
            zf.write(file_path, arcname=str(arcname))


def run(state):
    """
    Build the two ZIP archives under strict No-Default Policy:
     ZIP 1 — processed photos for video
       - source: processed_dir_video
       - target: processed_photos_zip_path

     ZIP 2 — magazine assets (Strictly requires verified real files at root)
       - source: book_to_publish directory
       - target: magazine_assets_zip_path
    """
    try:
        # ---------------------------------------------------------
        # ZIP 1 — processed photos for video
        # ---------------------------------------------------------
        processed_video_zip = Path(state.inputs["processed_photos_zip_path"])
        source_video_dir = (
            Path(state.processed_dir_video) 
            if hasattr(state, "processed_dir_video") and state.processed_dir_video 
            else Path("data/testing-input-output/processed_video")
        )
        zip_directory(source_video_dir, processed_video_zip)

        # ---------------------------------------------------------
        # ZIP 2 — magazine assets (Strict root-level PDF, Background, and Cover HTML)
        # ---------------------------------------------------------
        magazine_zip = Path(state.inputs["magazine_assets_zip_path"])
        publish_dir = (
            Path(state.book_to_publish_dir) 
            if hasattr(state, "book_to_publish_dir") and state.book_to_publish_dir 
            else Path("data/testing-input-output/book_to_publish")
        )

        if not publish_dir.exists() or not publish_dir.is_dir():
            raise FileNotFoundError(
                f"❌ NO-DEFAULT POLICY VIOLATION: Publication directory not found at '{publish_dir}'."
            )

        magazine_zip.parent.mkdir(parents=True, exist_ok=True)

        pdf_path = publish_dir / "magazine_content.pdf"
        bg_path = publish_dir / "cover_background.jpg"
        html_path = publish_dir / "magazine_cover.html"

        # Strict Validation Checks — NO dummies, NO placeholders, NO silent fallbacks allowed.
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"❌ NO-DEFAULT POLICY VIOLATION: Magazine content PDF is missing at '{pdf_path}'. "
                f"Expected output from 'generate_photo_pdf.py'."
            )
            
        if not bg_path.exists():
            raise FileNotFoundError(
                f"❌ NO-DEFAULT POLICY VIOLATION: Cover background image is missing at '{bg_path}'. "
                f"Expected output from image processing pipeline."
            )
            
        if not html_path.exists():
            raise FileNotFoundError(
                f"❌ NO-DEFAULT POLICY VIOLATION: Magazine cover HTML is missing at '{html_path}'. "
                f"Expected output from 'generate_cover.py'."
            )

        # Package verified real assets securely into the ZIP archive
        with zipfile.ZipFile(magazine_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(pdf_path, arcname="magazine_content.pdf")
            print("✅ Verified Asset Added: magazine_content.pdf")

            zf.write(bg_path, arcname="cover_background.jpg")
            print("✅ Verified Asset Added: cover_background.jpg")

            zf.write(html_path, arcname="magazine_cover.html")
            print("✅ Verified Asset Added: magazine_cover.html")

        # ---------------------------------------------------------
        # Update state results
        # ---------------------------------------------------------
        state.results["processed_photos_zip_path"] = str(processed_video_zip)
        state.results["magazine_assets_zip_path"] = str(magazine_zip)
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "error"
        state.results["error"] = str(e)
        print(f"❌ CRITICAL PIPELINE HALT in zip_builder: {e}")
        raise
