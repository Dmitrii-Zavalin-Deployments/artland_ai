# src/main.py
# Automated forensic patch: Suppress scikit-image low-contrast user warnings in test suites
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="skimage.*")

import argparse
import json
from pathlib import Path
from jsonschema import validate, ValidationError

from state import State
import frames_loader
import artistic_pipeline_video
import artistic_pipeline_magazine
import zip_builder


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Artland AI Pipeline Runner")
    parser.add_argument("--input_output_folder", required=True)
    parser.add_argument("--input_file_name", required=True)
    parser.add_argument("--output_file_name", required=True)
    args = parser.parse_args()

    base = Path(args.input_output_folder)

    input_json_path = base / args.input_file_name
    config_json_path = Path("config/config.json")
    output_json_path = base / args.output_file_name

    # Load JSONs with encoding
    input_data = load_json(input_json_path)
    config_data = load_json(config_json_path)

    # Validate schemas
    try:
        validate(input_data, load_schema("schema/input_schema.json"))
        validate(config_data, load_schema("schema/config_schema.json"))
    except ValidationError as e:
        error_state = {
            "inputs": input_data,
            "config": config_data,
            "results": {
                "status": "error",
                "error": str(e)
            }
        }
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(error_state, f, indent=2)
        print(f"❌ SCHEMA VALIDATION FAILED: {e}")
        return

    # Create state container
    state = State(input_data, config_data, args.input_output_folder)

    try:
        # 1️⃣ Load frames
        frames_loader.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            print(f"❌ Pipeline halted at frames_loader: {state.results.get('error')}")
            return

        # 2️⃣ Artistic pipeline for video (NO fading edges)
        artistic_pipeline_video.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            print(f"❌ Pipeline halted at artistic_pipeline_video: {state.results.get('error')}")
            return

        # 3️⃣ Artistic pipeline for magazine (WITH fading edges + background + PDF)
        artistic_pipeline_magazine.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            print(f"❌ Pipeline halted at artistic_pipeline_magazine: {state.results.get('error')}")
            return

        # 4️⃣ Build ZIP archives
        zip_builder.run(state)
        if state.results.get("status") == "error":
            state.write_output_json(output_json_path)
            print(f"❌ Pipeline halted at zip_builder: {state.results.get('error')}")
            return

    except Exception as e:
        state.results["status"] = "error"
        state.results["error"] = str(e)
        state.write_output_json(output_json_path)
        print(f"❌ CRITICAL PIPELINE EXCEPTION: {e}")
        raise

    # Write final successful output.json
    state.write_output_json(output_json_path)
    print("🎯 Pipeline completed successfully with all verified assets.")


if __name__ == "__main__":
    main()
