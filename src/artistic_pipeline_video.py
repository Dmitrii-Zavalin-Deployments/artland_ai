# src/artistic_pipeline_video.py
import shutil
import subprocess
from pathlib import Path


def run(state):
    """
    Produce ZIP 1 (video‑ready photos).
    Steps:
      - For each original frame:
          * copy to photo.jpg
          * run artistic_painting_processor.py
          * DO NOT run add_fading_edges.py
          * save output to processed_dir_video/<name>.jpg
    """

    try:
        for frame_path in state.frame_paths:
            # Temporary working file expected by the existing scripts
            temp_input = state.original_dir / "photo.jpg"

            # Copy original frame into working file
            shutil.copy(frame_path, temp_input)

            # Run ONLY the artistic painting processor
            subprocess.run(
                ["python3", "artistic_painting_processor.py"],
                check=True
            )

            # Save the processed result into the video directory
            output_path = state.processed_dir_video / (frame_path.stem + ".jpg")
            shutil.copy(temp_input, output_path)

            # Track processed file
            state.processed_frame_paths_video.append(output_path)

        # Mark success
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

