# src/artistic_pipeline_video.py
import shutil
from pathlib import Path

from processor import artistic_painting_processor


def run(state):
    """
    Produce ZIP 1 (video-ready photos).
    Steps:
      - Ensure working directories exist
      - For each original frame:
          * safely copy to working directory (`state.original_dir / frame_path.name`)
          * set `state.current_frame_path`
          * run artistic_painting_processor.run(state)
          * DO NOT run add_fading_edges.py
          * strictly verify and save output to processed_dir_video/<name>.jpg
    Enforces No-Default Policy: Fails immediately if processors or outputs are missing.
    """
    try:
        # Ensure working directories exist
        state.processed_dir_video.mkdir(parents=True, exist_ok=True)
        state.original_dir.mkdir(parents=True, exist_ok=True)

        state.processed_frame_paths_video = []

        if not hasattr(state, "frame_paths") or not state.frame_paths:
            raise ValueError("❌ NO-DEFAULT POLICY VIOLATION: No frames found in state.frame_paths for video pipeline.")

        for frame_path in state.frame_paths:
            frame_path = Path(frame_path)
            working_frame_path = state.original_dir / frame_path.name

            # Guard against shutil.SameFileError if source and destination are identical
            if frame_path.resolve() != working_frame_path.resolve():
                shutil.copy(frame_path, working_frame_path)

            # Assign dynamic frame path to state for active processors
            state.current_frame_path = working_frame_path

            # Run the artistic painting processor via direct method invocation
            if not hasattr(artistic_painting_processor, "run"):
                raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'artistic_painting_processor' lacks a 'run' method.")
            
            artistic_painting_processor.run(state)

            # Strict No-Default Check: Processor must have produced the processed working file
            if not working_frame_path.exists():
                raise FileNotFoundError(
                    f"❌ NO-DEFAULT POLICY VIOLATION: Artistic painting processor failed to generate output at '{working_frame_path}'."
                )

            # Save the verified processed result into the video directory
            output_path = state.processed_dir_video / (frame_path.stem + ".jpg")
            if working_frame_path.resolve() != output_path.resolve():
                shutil.copy(working_frame_path, output_path)

            # Track processed file
            state.processed_frame_paths_video.append(output_path)

        # Mark success
        state.results["status"] = "success"
        state.results["error"] = ""

    except Exception as e:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "error"
        state.results["error"] = str(e)
        print(f"❌ CRITICAL PIPELINE HALT in artistic_pipeline_video: {e}")
        raise
