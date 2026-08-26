# src/state.py
import json
from pathlib import Path
from datetime import datetime, timezone

class State:
    def __init__(self, inputs, config, input_output_folder):
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

    def write_output_json(self, output_json_path):
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
        with open(out_path, "w") as f:
            json.dump(output_data, f, indent=2)
