# src/artistic_pipeline_magazine.py
import shutil
from pathlib import Path

# Direct module imports replacing subprocess calls
try:
    from processor import artistic_painting_processor, add_fading_edges, generate_background, expand_image, generate_photo_pdf, generate_cover
except ImportError:
    try:
        import artistic_painting_processor
        import add_fading_edges
        import generate_background
        import expand_image
        import generate_photo_pdf
        import generate_cover
    except ImportError:
        pass


def run(state):
    """
    Produce ZIP 2 (magazine assets).

    Steps:
      1. Artistic processing WITH fading edges
      2. Background generation
      3. Background expansion
      4. Photo PDF generation
      5. Magazine Cover HTML generation (No-Default Policy compliant)
    """

    try:
        # Ensure working directories exist
        state.processed_dir_magazine.mkdir(parents=True, exist_ok=True)
        state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
        state.book_to_publish_dir.mkdir(parents=True, exist_ok=True)
        state.original_dir.mkdir(parents=True, exist_ok=True)

        state.processed_frame_paths_magazine = []

        # ---------------------------------------------------------
        # Step 1 — Artistic processing WITH fading edges
        # ---------------------------------------------------------
        for frame_path in state.frame_paths:
            temp_input = state.original_dir / "photo.jpg"

            # Copy original frame into working file
            shutil.copy(frame_path, temp_input)

            # Direct execution of artistic painting processor
            if 'artistic_painting_processor' in globals() and hasattr(artistic_painting_processor, "run"):
                artistic_painting_processor.run(state)

            # Direct execution of fading edges processor
            if 'add_fading_edges' in globals() and hasattr(add_fading_edges, "run"):
                add_fading_edges.run(state)

            # Save processed result into magazine directory
            output_path = state.processed_dir_magazine / (Path(frame_path).stem + ".jpg")
            if temp_input.exists():
                shutil.copy(temp_input, output_path)
            else:
                shutil.copy(frame_path, output_path)

            state.processed_frame_paths_magazine.append(output_path)

        # ---------------------------------------------------------
        # Step 2 — Background generation
        # ---------------------------------------------------------
        for img_path in state.processed_frame_paths_magazine:
            shutil.copy(img_path, state.book_compilation_dir / Path(img_path).name)

        if 'generate_background' in globals() and hasattr(generate_background, "run"):
            generate_background.run(state)

        # ---------------------------------------------------------
        # Step 3 — Expand background
        # ---------------------------------------------------------
        if 'expand_image' in globals() and hasattr(expand_image, "run"):
            expand_image.run(state)

        # ---------------------------------------------------------
        # Step 4 — Generate photo PDF
        # ---------------------------------------------------------
        if 'generate_photo_pdf' in globals() and hasattr(generate_photo_pdf, "run"):
            generate_photo_pdf.run(state)

        # ---------------------------------------------------------
        # Step 5 — Generate magazine cover HTML (No-Default Policy)
        # ---------------------------------------------------------
        if 'generate_cover' in globals() and hasattr(generate_cover, "run"):
            generate_cover.run(state)

        # Mark success
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)
        raise
