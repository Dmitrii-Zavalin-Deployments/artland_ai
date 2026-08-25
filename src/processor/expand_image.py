# src/processor/expand_image.py
from PIL import Image
from pathlib import Path

def expand_background_image(image_path, scale_factor_y, num_repeats_x):
    """
    Scales an image vertically and repeats it horizontally to form a wide background,
    using parameters retrieved strictly from configuration.
    """
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found at: {image_path}")

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
            print(f"[DEBUG] Image successfully expanded and saved to: {image_path}")

    except Exception as e:
        print(f"[DEBUG] An error occurred in expand_image: {e}")
        raise RuntimeError(f"[ERROR] Error expanding image: {e}")


def run(state=None):
    """
    Pipeline execution entry point called by artistic_pipeline_magazine.py.
    """
    image_path = Path("data/testing-input-output/book_compilation/cover_background.jpg")
    scale_factor_y = None
    num_repeats_x = None

    if state:
        if hasattr(state, "book_compilation_dir"):
            p1 = Path(state.book_compilation_dir) / "cover_background.jpg"
            p2 = Path(state.book_compilation_dir) / "background.jpg"
            image_path = p1 if p1.exists() else (p2 if p2.exists() else p1)
        
        if hasattr(state, "config") and isinstance(state.config, dict):
            cfg = state.config.get("expand_image", {})
            scale_factor_y = cfg.get("scale_factor_y")
            num_repeats_x = cfg.get("num_repeats_x")

    # Enforce No-Default Policy
    if scale_factor_y is None or num_repeats_x is None:
        raise ValueError("❌ No-Default Policy Error: Required 'expand_image' config fields (scale_factor_y, num_repeats_x) missing from config.json.")

    expand_background_image(image_path, scale_factor_y, num_repeats_x)


if __name__ == "__main__":
    test_config = {
        "scale_factor_y": 10,
        "num_repeats_x": 10
    }
    image_path = "book_compilation/background.jpg"
    expand_background_image(image_path, test_config["scale_factor_y"], test_config["num_repeats_x"])
    print("Image successfully expanded and replaced in book_compilation!")
