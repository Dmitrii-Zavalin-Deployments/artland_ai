# src/artistic_pipeline_magazine.py
import shutil
import subprocess
from pathlib import Path


def run(state):
    """
    Produce ZIP 2 (magazine assets).

    Steps:
      1. Artistic processing WITH fading edges
      2. Background generation (generate_background.py)
      3. Background expansion (expand_image.py)
      4. Photo PDF generation (generate_photo_pdf.py)
    """

    try:
        # ---------------------------------------------------------
        # Step 1 — Artistic processing WITH fading edges
        # ---------------------------------------------------------
        for frame_path in state.frame_paths:
            temp_input = state.original_dir / "photo.jpg"

            # Copy original frame into working file
            shutil.copy(frame_path, temp_input)

            # Run artistic painting processor
            subprocess.run(
                ["python3", "artistic_painting_processor.py"],
                check=True
            )

            # Run fading edges
            subprocess.run(
                ["python3", "add_fading_edges.py"],
                check=True
            )

            # Save processed result into magazine directory
            output_path = state.processed_dir_magazine / (frame_path.stem + ".jpg")
            shutil.copy(temp_input, output_path)

            state.processed_frame_paths_magazine.append(output_path)

        # ---------------------------------------------------------
        # Step 2 — Background generation
        # ---------------------------------------------------------
        # Copy processed images into book_compilation
        for img_path in state.processed_frame_paths_magazine:
            shutil.copy(img_path, state.book_compilation_dir / img_path.name)

        # Run background generator
        subprocess.run(
            ["python3", "generate_background.py"],
            check=True
        )

        # ---------------------------------------------------------
        # Step 3 — Expand background
        # ---------------------------------------------------------
        subprocess.run(
            ["python3", "expand_image.py"],
            check=True
        )

        # ---------------------------------------------------------
        # Step 4 — Generate photo PDF
        # ---------------------------------------------------------
        subprocess.run(
            ["python3", "generate_photo_pdf.py"],
            check=True
        )

        # Mark success
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

