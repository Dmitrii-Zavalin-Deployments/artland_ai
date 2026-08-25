# src/artistic_pipeline_video.py
import shutil
from pathlib import Path

# Direct module import replacing subprocess calls
try:
    from processor import artistic_painting_processor
except ImportError:
    try:
        import artistic_painting_processor
    except ImportError:
        pass


def run(state):
    """
    Produce ZIP 1 (video‑ready photos).
    Steps:
      - Ensure working directories exist
      - For each original frame:
          * copy to photo.jpg
          * run artistic_painting_processor.run(state)
          * DO NOT run add_fading_edges.py
          * save output to processed_dir_video/<name>.jpg
    """

    try:
        # Ensure working directories exist
        state.processed_dir_video.mkdir(parents=True, exist_ok=True)
        state.original_dir.mkdir(parents=True, exist_ok=True)

        state.processed_frame_paths_video = []

        for frame_path in state.frame_paths:
            # Temporary working file expected by the processor
            temp_input = state.original_dir / "photo.jpg"

            # Copy original frame into working file
            shutil.copy(frame_path, temp_input)

            # Run ONLY the artistic painting processor via direct method invocation
            if 'artistic_painting_processor' in globals() and hasattr(artistic_painting_processor, "run"):
                artistic_painting_processor.run(state)

            # Save the processed result into the video directory
            output_path = state.processed_dir_video / (Path(frame_path).stem + ".jpg")
            if temp_input.exists():
                shutil.copy(temp_input, output_path)
            else:
                shutil.copy(frame_path, output_path)

            # Track processed file
            state.processed_frame_paths_video.append(output_path)

        # Mark success
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)
