# src/artistic_pipeline_magazine.py
import shutil
from pathlib import Path

from processor import (
    add_fading_edges,
    artistic_painting_processor,
    expand_image,
    generate_background,
    generate_cover,
    generate_photo_pdf,
)


def run(state):
    """
    Produce ZIP 2 (magazine assets).

    Steps:
      1. Artistic processing WITH fading edges
      2. Background generation
      3. Background expansion
      4. Photo PDF generation
      5. Magazine Cover HTML generation (No-Default Policy compliant)

    Enforces No-Default Policy: Fails loud and fast if any processor or asset is missing.
    """
    try:
        # Ensure working directories exist
        state.processed_dir_magazine.mkdir(parents=True, exist_ok=True)
        state.book_compilation_dir.mkdir(parents=True, exist_ok=True)
        state.book_to_publish_dir.mkdir(parents=True, exist_ok=True)
        state.original_dir.mkdir(parents=True, exist_ok=True)

        state.processed_frame_paths_magazine = []

        if not hasattr(state, "frame_paths") or not state.frame_paths:
            raise ValueError("❌ NO-DEFAULT POLICY VIOLATION: No frames found in state.frame_paths for magazine pipeline.")

        # ---------------------------------------------------------
        # Step 1 — Artistic processing WITH fading edges
        # ---------------------------------------------------------
        for frame_path in state.frame_paths:
            frame_path = Path(frame_path)
            working_frame_path = state.original_dir / frame_path.name

            # Guard against shutil.SameFileError if source and destination are identical
            if frame_path.resolve() != working_frame_path.resolve():
                shutil.copy(frame_path, working_frame_path)

            # Assign dynamic frame path to state for active processors
            state.current_frame_path = working_frame_path

            # Direct execution of artistic painting processor
            if not hasattr(artistic_painting_processor, "run"):
                raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'artistic_painting_processor' lacks a 'run' method.")
            artistic_painting_processor.run(state)

            # Direct execution of fading edges processor
            if not hasattr(add_fading_edges, "run"):
                raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'add_fading_edges' lacks a 'run' method.")
            add_fading_edges.run(state)

            # Strict check that working file exists after processing
            if not working_frame_path.exists():
                raise FileNotFoundError(
                    f"❌ NO-DEFAULT POLICY VIOLATION: Processed working file missing at '{working_frame_path}' after processing steps."
                )

            # Save processed result into magazine directory
            output_path = state.processed_dir_magazine / (frame_path.stem + ".jpg")
            if working_frame_path.resolve() != output_path.resolve():
                shutil.copy(working_frame_path, output_path)

            state.processed_frame_paths_magazine.append(output_path)

        # ---------------------------------------------------------
        # Step 2 — Background generation
        # ---------------------------------------------------------
        for img_path in state.processed_frame_paths_magazine:
            target_bg_path = state.book_compilation_dir / Path(img_path).name
            if Path(img_path).resolve() != target_bg_path.resolve():
                shutil.copy(img_path, target_bg_path)

        if not hasattr(generate_background, "run"):
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'generate_background' lacks a 'run' method.")
        generate_background.run(state)

        # ---------------------------------------------------------
        # Step 3 — Expand background
        # ---------------------------------------------------------
        if not hasattr(expand_image, "run"):
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'expand_image' lacks a 'run' method.")
        expand_image.run(state)

        # ---------------------------------------------------------
        # Step 4 — Generate photo PDF
        # ---------------------------------------------------------
        if not hasattr(generate_photo_pdf, "run"):
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'generate_photo_pdf' lacks a 'run' method.")
        generate_photo_pdf.run(state)

        # ---------------------------------------------------------
        # Step 5 — Generate magazine cover HTML (No-Default Policy)
        # ---------------------------------------------------------
        if not hasattr(generate_cover, "run"):
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'generate_cover' lacks a 'run' method.")
        generate_cover.run(state)

        # Mark success
        state.results["status"] = "success"
        state.results["error"] = ""

    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "error"
        state.results["error"] = str(e)
        print(f"❌ CRITICAL PIPELINE HALT in artistic_pipeline_magazine: {e}")
        raise
