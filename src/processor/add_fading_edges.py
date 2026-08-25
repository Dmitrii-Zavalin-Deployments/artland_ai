# src/processor/add_fading_edges.py
import cv2
import numpy as np
import os
from pathlib import Path

def apply_proportional_whitening(input_image_path, config=None):
    """
    Places a painting onto a white canvas and applies gradual whitening and blurring
    to the edges with proportions retrieved strictly from config (No-Default Policy).
    """
    try:
        if not os.path.exists(input_image_path):
            print(f"[ERROR] File not found: '{input_image_path}'")
            return

        # Load the artistic painting
        image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Failed to load image from {input_image_path}")
        print("[DEBUG] Artistic painting loaded successfully for fading edges.")

        height, width, _ = image.shape

        # Enforce No-Default Policy for configuration parameters
        cfg = config or {}
        if not isinstance(cfg, dict):
            cfg = {}

        a4_width = cfg.get("canvas_width")
        a4_height = cfg.get("canvas_height")
        tb_divisor = cfg.get("top_bottom_divisor")
        lr_divisor = cfg.get("left_right_divisor")

        # If missing from config, raise deterministic No-Default Policy error
        missing = [k for k, v in [
            ("canvas_width", a4_width), 
            ("canvas_height", a4_height), 
            ("top_bottom_divisor", tb_divisor), 
            ("left_right_divisor", lr_divisor)
        ] if v is None]

        if missing:
            raise ValueError(f"❌ No-Default Policy Error: Required fading_edges config fields missing from config.json: {missing}")

        a4_width = int(a4_width)
        a4_height = int(a4_height)
        tb_divisor = int(tb_divisor)
        lr_divisor = int(lr_divisor)

        # White canvas background
        a4_canvas = np.ones((a4_height, a4_width, 3), dtype=np.uint8) * 255

        # Resize the painting while maintaining aspect ratio
        scale_factor = min(a4_width / width, a4_height / height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image_resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Center painting on canvas
        x_offset = (a4_width - new_width) // 2
        y_offset = (a4_height - new_height) // 2
        a4_canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = image_resized

        # Create gradient masks for whitening effects
        top_bottom_mask = np.zeros((a4_height, a4_width), dtype=np.float32)
        left_right_mask = np.zeros((a4_height, a4_width), dtype=np.float32)

        top_bottom_max_distance = a4_height // tb_divisor
        left_right_max_distance = a4_width // lr_divisor

        for y in range(a4_height):
            for x in range(a4_width):
                top_bottom_distance = min(y, a4_height - y)
                top_bottom_mask[y, x] = max(0, 1 - top_bottom_distance / top_bottom_max_distance)

        for y in range(a4_height):
            for x in range(a4_width):
                left_right_distance = min(x, a4_width - x)
                left_right_mask[y, x] = max(0, 1 - left_right_distance / left_right_max_distance)

        # Combine masks and apply smooth Gaussian blur
        combined_mask = np.maximum(top_bottom_mask, left_right_mask)
        combined_mask = cv2.GaussianBlur(combined_mask, (101, 101), 50)

        # Apply gradient mask to blend edges into white
        blurred_canvas = cv2.GaussianBlur(a4_canvas, (31, 31), 15)
        for c in range(3):
            a4_canvas[:, :, c] = (a4_canvas[:, :, c] * (1 - combined_mask) + blurred_canvas[:, :, c] * combined_mask).astype(np.uint8)

        # Overwrite input path for pipeline tracking
        cv2.imwrite(input_image_path, a4_canvas)
        print(f"[DEBUG] Proportional whitened edges applied and saved to: {input_image_path}")

    except Exception as e:
        print(f"[DEBUG] An error occurred in add_fading_edges: {e}")
        raise RuntimeError(f"[ERROR] Error processing fading edges: {e}")


def run(state=None):
    """
    Pipeline execution entry point called by artistic_pipeline_magazine.py.
    """
    input_image_path = "data/testing-input-output/original/photo.jpg"
    config = {}

    if state:
        if hasattr(state, "original_dir"):
            input_image_path = str(Path(state.original_dir) / "photo.jpg")
        if hasattr(state, "config") and isinstance(state.config, dict):
            config = state.config.get("fading_edges", {})

    apply_proportional_whitening(input_image_path, config=config)


if __name__ == "__main__":
    # Fallback config for standalone execution
    test_config = {
        "canvas_width": 2480,
        "canvas_height": 3508,
        "top_bottom_divisor": 4,
        "left_right_divisor": 8
    }
    input_image_path = "converted_sketches/refined_artistic_painting.jpg"
    print(f"[DEBUG] Starting proportional whitening and blurring process for: {input_image_path}")
    apply_proportional_whitening(input_image_path, config=test_config)
    print("[DEBUG] Proportional whitening and blurring process completed successfully.")
