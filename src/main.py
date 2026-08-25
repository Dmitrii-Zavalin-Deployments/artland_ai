# src/main.py
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
    with open(path) as f:
        return json.load(f)


def load_schema(path):
    with open(path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_output_folder", required=True)
    parser.add_argument("--input_file_name", required=True)
    parser.add_argument("--output_file_name", required=True)
    args = parser.parse_args()

    base = Path(args.input_output_folder)

    input_json_path = base / args.input_file_name
    config_json_path = Path("config/config.json")
    output_json_path = base / args.output_file_name

    # Load JSONs
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
        with open(output_json_path, "w") as f:
            json.dump(error_state, f, indent=2)
        return

    # Create state container
    state = State(input_data, config_data, args.input_output_folder)

    # 1️⃣ Load frames
    frames_loader.run(state)
    if state.results["status"] == "error":
        state.write_output_json(output_json_path)
        return

    # 2️⃣ Artistic pipeline for video (NO fading edges)
    artistic_pipeline_video.run(state)
    if state.results["status"] == "error":
        state.write_output_json(output_json_path)
        return

    # 3️⃣ Artistic pipeline for magazine (WITH fading edges + background + PDF)
    artistic_pipeline_magazine.run(state)
    if state.results["status"] == "error":
        state.write_output_json(output_json_path)
        return

    # 4️⃣ Build ZIP archives
    zip_builder.run(state)

    # Write final output.json
    state.write_output_json(output_json_path)


if __name__ == "__main__":
    main()

