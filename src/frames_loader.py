# src/frames_loader.py
import zipfile
from pathlib import Path

def run(state):
    """
    Unzip the input archive and collect all .jpg/.png files
    into state.frame_paths.
    """

    zip_path = state.inputs["input_zip_path"]

    try:
        # Extract all files from the input ZIP
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(state.original_dir)

        # Collect valid image files
        for frame in sorted(state.original_dir.glob("*")):
            if frame.suffix.lower() in [".jpg", ".png"]:
                state.frame_paths.append(frame)

        # Error if no images found
        if not state.frame_paths:
            state.results["status"] = "error"
            state.results["error"] = "No JPG/PNG frames found in input ZIP."

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)

