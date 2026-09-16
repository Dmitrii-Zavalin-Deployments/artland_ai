# src/main.py
# Automated forensic patch: Suppress scikit-image low-contrast user warnings in test suites
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="skimage.*")

import argparse
import json
import logging
import sys
from pathlib import Path

from jsonschema import ValidationError, validate

# Ensure the parent directory is in sys.path to guarantee flawless package resolution
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))

try:
    from . import (
        artistic_pipeline_magazine,
        artistic_pipeline_video,
        frames_loader,
        zip_builder,
    )
    from .state import State
except ImportError:
    import artistic_pipeline_magazine
    import artistic_pipeline_video
    import frames_loader
    import zip_builder
    from state import State

logger = logging.getLogger(__name__)


def load_json(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Required JSON file not found at path: {path}")
    logger.debug("Loading JSON from file: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_schema(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Required schema file not found at path: {path}")
    logger.debug("Loading schema from file: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # Configure global logging level only if not already configured (preserving pytest stream capture)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    parser = argparse.ArgumentParser(description="Artland AI Pipeline Runner")
    parser.add_argument("--input_output_folder", required=True)
    parser.add_argument("--input_file_name", required=True)
    parser.add_argument("--output_file_name", required=True)
    args = parser.parse_args()

    logger.info("Initializing main pipeline runner with folder: %s", args.input_output_folder)
    base = Path(args.input_output_folder)

    input_json_path = base / args.input_file_name
    config_json_path = Path("config/config.json")
    output_json_path = base / args.output_file_name

    try:
        # Load JSONs with encoding and existence checking
        logger.info("Loading input configuration and operational payloads...")
        input_data = load_json(input_json_path)
        config_data = load_json(config_json_path)

        # Validate schemas
        logger.info("Validating input and config JSON schemas.")
        validate(input_data, load_schema("schema/input_schema.json"))
        validate(config_data, load_schema("schema/config_schema.json"))
        
    except (ValidationError, FileNotFoundError, json.JSONDecodeError) as e:
        error_state = {
            "inputs": locals().get("input_data", {}),
            "config": locals().get("config_data", {}),
            "results": {
                "status": "error",
                "error": str(e)
            }
        }
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(error_state, f, indent=2)
        logger.error("❌ SCHEMA VALIDATION OR LOADING FAILED: %s", e)
        return

    # Create state container
    state = State(input_data, config_data, args.input_output_folder)

    try:
        # 1️⃣ Load frames
        logger.info("Step 1: Executing frames_loader pipeline.")
        frames_loader.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            logger.error("❌ Pipeline halted at frames_loader: %s", state.results.get('error'))
            return

        # 2️⃣ Artistic pipeline for video (NO fading edges)
        logger.info("Step 2: Executing artistic_pipeline_video.")
        artistic_pipeline_video.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            logger.error("❌ Pipeline halted at artistic_pipeline_video: %s", state.results.get('error'))
            return

        # 3️⃣ Artistic pipeline for magazine (WITH fading edges + background + PDF)
        logger.info("Step 3: Executing artistic_pipeline_magazine.")
        artistic_pipeline_magazine.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            logger.error("❌ Pipeline halted at artistic_pipeline_magazine: %s", state.results.get('error'))
            return

        # 4️⃣ Build ZIP archives
        logger.info("Step 4: Executing zip_builder.")
        zip_builder.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            logger.error("❌ Pipeline halted at zip_builder: %s", state.results.get('error'))
            return

    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["status"] = "error"
        state.results["error"] = str(e)
        state.write_output_json(output_json_path)
        logger.exception("❌ CRITICAL PIPELINE EXCEPTION")
        raise

    # Write final successful output.json
    state.write_output_json(output_json_path)
    logger.info("🎯 Pipeline completed successfully with all verified assets.")


if __name__ == "__main__":  # pragma: no cover
    main()
