# src/state.py
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class State:
    def __init__(self, inputs, config, input_output_folder):
        logger.info("Initializing State management instance.")
        if not isinstance(inputs, dict):
            raise TypeError("❌ NO-DEFAULT POLICY VIOLATION: 'inputs' must be a valid dictionary.")
        if not isinstance(config, dict):
            raise TypeError("❌ NO-DEFAULT POLICY VIOLATION: 'config' must be a valid dictionary.")
        if not input_output_folder:
            raise ValueError("❌ NO-DEFAULT POLICY VIOLATION: 'input_output_folder' is missing or empty.")

        self.inputs = inputs
        self.config = config
        self.results = {
            "date_time": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "error": ""
        }
        
        # Base input/output working folder
        base_dir = Path(input_output_folder)
        
        # Internal directories
        self.original_dir = base_dir / "original"
        self.processed_dir_video = base_dir / "processed_video"
        self.processed_dir_magazine = base_dir / "processed_magazine"
        self.book_compilation_dir = base_dir / "book_compilation"
        self.book_to_publish_dir = base_dir / "book_to_publish"
        
        # Frame and artifact collections
        self.frame_paths = []
        self.processed_frame_paths_video = []
        self.processed_frame_paths_magazine = []
        
        # Dynamic per-frame path tracker for active processors
        self.current_frame_path = None
        logger.debug("State initialized successfully with base directory: %s", base_dir)

    def write_output_json(self, output_json_path):
        try:
            # Ensure date_time is present and up to date when writing output
            if "date_time" not in self.results:
                self.results["date_time"] = datetime.now(timezone.utc).isoformat()
                
            output_data = {
                "inputs": self.inputs,
                "config": self.config,
                "results": self.results
            }
            out_path = Path(output_json_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Writing output JSON to path: %s", out_path)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2)
        except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
            logger.exception("❌ CRITICAL EXCEPTION writing output JSON: %s", e)
            raise RuntimeError(f"Could not write output JSON to {output_json_path}: {e}") from e
