# src/processor/expand_image.py
from pathlib import Path

from PIL import Image


def expand_background_image(image_path, scale_factor_y, num_repeats_x):
    """
    Scales an image vertically and repeats it horizontally to form a wide background,
    using parameters retrieved strictly from configuration.
    Enforces No-Default Policy.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Background image not found at '{image_path}'."
        )

    # Load the original image
    with Image.open(image_path) as original_image:
        width, height = original_image.size

        # Scale the image vertically using bicubic interpolation
        scaled_height = height * int(scale_factor_y)
        scaled_image = original_image.resize((width, scaled_height), Image.Resampling.BICUBIC)

        # Create a new blank image for horizontal duplication
        expanded_width = width * int(num_repeats_x)
        new_image = Image.new("RGB", (expanded_width, scaled_height))

        # Paste the scaled image multiple times horizontally
        for i in range(int(num_repeats_x)):
            new_image.paste(scaled_image, (i * width, 0))

        # Overwrite the original image file
        new_image.save(image_path)
        print(f"✅ Image successfully expanded and saved to: {image_path}")


def run(state=None):
    """
    Pipeline execution entry point called by artistic_pipeline_magazine.py.
    Enforces strict state and config validation.
    """
    try:
        if not state:
            raise ValueError("❌ NO-DEFAULT POLICY VIOLATION: 'state' object is required for expand_image execution.")
        
        if not hasattr(state, "book_compilation_dir"):
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'state' object lacks 'book_compilation_dir' attribute.")

        # Strict target path verification
        image_path = Path(state.book_compilation_dir) / "cover_background.jpg"
        alt_path = Path(state.book_compilation_dir) / "background.jpg"
        
        if not image_path.exists():
            if alt_path.exists():
                image_path = alt_path
            else:
                raise FileNotFoundError(
                    f"❌ NO-DEFAULT POLICY VIOLATION: Cover background image not found at '{image_path}' or '{alt_path}'."
                )

        if not hasattr(state, "config") or not isinstance(state.config, dict):
            raise KeyError("❌ NO-DEFAULT POLICY VIOLATION: 'state.config' dictionary is missing or invalid.")

        cfg = state.config.get("expand_image")
        if not cfg or not isinstance(cfg, dict):
            raise KeyError("❌ NO-DEFAULT POLICY VIOLATION: 'expand_image' configuration block is missing from config.json.")

        scale_factor_y = cfg.get("scale_factor_y")
        num_repeats_x = cfg.get("num_repeats_x")

        # Enforce No-Default Policy for configuration fields
        missing = [k for k, v in [
            ("scale_factor_y", scale_factor_y),
            ("num_repeats_x", num_repeats_x)
        ] if v is None]

        if missing:
            raise ValueError(
                f"❌ NO-DEFAULT POLICY VIOLATION: Required 'expand_image' config fields missing from config.json: {missing}. "
                f"No default values allowed."
            )

        expand_background_image(image_path, scale_factor_y, num_repeats_x)

    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        print(f"❌ CRITICAL PIPELINE HALT in expand_image: {e}")
        raise RuntimeError(f"[ERROR] Error expanding image: {e}")