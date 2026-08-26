# src/frames_loader.py
import logging
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


def run(state):
    """
    Unzip the input archive and collect all .jpg/.png files
    into state.frame_paths (supporting nested directories).
    Enforces No-Default Policy: Fails immediately if input ZIP is missing or empty.
    """
    logger.info("Starting frames loader pipeline execution.")
    try:
        # Check if input_zip_path is specified in state inputs
        if not hasattr(state, "inputs") or not state.inputs or "input_zip_path" not in state.inputs:
            raise KeyError("Required key 'input_zip_path' is missing from state inputs.")

        zip_path = Path(state.inputs["input_zip_path"])
        if not zip_path.exists():
            raise FileNotFoundError(f"Input ZIP file not found at: {zip_path}")

        # Ensure original directory exists
        logger.debug("Ensuring original directory exists at: %s", state.original_dir)
        state.original_dir.mkdir(parents=True, exist_ok=True)

        # Extract all files from the input ZIP
        logger.info("Extracting input ZIP archive from %s to %s", zip_path, state.original_dir)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(state.original_dir)

        # Collect valid image files recursively (handles nested folders inside zip)
        state.frame_paths = []
        for frame in sorted(state.original_dir.glob("**/*")):
            if frame.is_file() and frame.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                state.frame_paths.append(frame)

        logger.info("Discovered %d valid image frame(s) in input ZIP.", len(state.frame_paths))

        # Strict No-Default Check: Raise loud error if no images found
        if not state.frame_paths:
            raise ValueError(
                f"❌ NO-DEFAULT POLICY VIOLATION: No valid JPG/PNG frames found in input ZIP '{zip_path}'. "
                f"Extraction directory '{state.original_dir}' contains no supported image assets."
            )

        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "success"
        state.results["error"] = ""
        logger.info("Frames loader pipeline completed successfully.")

    except (zipfile.BadZipFile, OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError, Exception) as e:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "error"
        state.results["error"] = str(e)
        logger.exception("❌ CRITICAL PIPELINE HALT in frames_loader")
        raise
