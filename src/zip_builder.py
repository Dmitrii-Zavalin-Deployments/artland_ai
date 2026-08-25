# src/zip_builder.py
import zipfile
from pathlib import Path


def zip_directory(source_dir: Path, zip_path: Path):
    """Utility: zip all files inside a directory."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.glob("**/*")):
            if file_path.is_file():
                # Store relative paths inside the ZIP
                arcname = file_path.relative_to(source_dir)
                zf.write(file_path, arcname=str(arcname))


def run(state):
    """
    Build the two ZIP archives:

      ZIP 1 — processed photos for video
        - source: processed_dir_video
        - target: processed_photos_zip_path

      ZIP 2 — magazine assets
        - source: book_compilation + book_to_publish
        - target: magazine_assets_zip_path
    """

    try:
        # ---------------------------------------------------------
        # ZIP 1 — processed photos for video
        # ---------------------------------------------------------
        processed_video_zip = Path(state.inputs["processed_photos_zip_path"])
        zip_directory(state.processed_dir_video, processed_video_zip)

        # ---------------------------------------------------------
        # ZIP 2 — magazine assets
        # ---------------------------------------------------------
        magazine_zip = Path(state.inputs["magazine_assets_zip_path"])

        with zipfile.ZipFile(magazine_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add book_compilation assets
            for file_path in sorted(state.book_compilation_dir.glob("**/*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(state.book_compilation_dir)
                    zf.write(file_path, arcname=f"book_compilation/{arcname}")

            # Add book_to_publish assets
            for file_path in sorted(state.book_to_publish_dir.glob("**/*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(state.book_to_publish_dir)
                    zf.write(file_path, arcname=f"book_to_publish/{arcname}")

        # ---------------------------------------------------------
        # Update state results
        # ---------------------------------------------------------
        state.results["processed_photos_zip_path"] = str(processed_video_zip)
        state.results["magazine_assets_zip_path"] = str(magazine_zip)
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

