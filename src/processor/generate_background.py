# src/processor/generate_background.py
import logging
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


def extract_colors_from_image(image_path, num_colors, brightness_threshold):
    """Extracts dominant colors from a single image using config parameters."""
    image_path = Path(image_path)
    logger.debug("Checking image path for color extraction: %s", image_path)
    if not image_path.exists():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Image not found at '{image_path}'."
        )

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"❌ NO-DEFAULT POLICY VIOLATION: Failed to read image from '{image_path}' via OpenCV.")
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    reshaped_image = image.reshape(-1, 3)

    # Use KMeans to find dominant colors
    kmeans = KMeans(n_clusters=int(num_colors), random_state=42, n_init=10)
    kmeans.fit(reshaped_image)
    colors = kmeans.cluster_centers_.astype(int)

    # Filter and store light colors
    filtered_colors = []
    for color in colors:
        hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
        if hsv[2] > int(brightness_threshold):  # V-channel brightness check
            filtered_colors.append(color.tolist())
            
    logger.debug("Colors extracted from %s: %s", image_path, filtered_colors)
    return filtered_colors


def process_images(image_folder, num_colors, brightness_threshold):
    """Loops through images, extracts colors, and accumulates unique colors."""
    image_folder = Path(image_folder)
    logger.debug("Processing images in folder: %s", image_folder)
    if not image_folder.exists():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Image folder not found at '{image_folder}'."
        )

    image_files = sorted(list(image_folder.glob("*.jpg")) + list(image_folder.glob("*.png")))
    if not image_files:
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: No image files (*.jpg, *.png) found in folder '{image_folder}'."
        )

    unique_colors = []
    for image_path in image_files:
        extracted = extract_colors_from_image(image_path, num_colors, brightness_threshold)
        unique_colors.extend(extracted)
        
    logger.debug("Updated unique color list: %s", unique_colors)
    return unique_colors


def group_colors_by_lightness(colors):
    """Reorders colors so lighter shades move toward the top and darker ones toward the bottom."""
    if not colors:
        return colors
    colors_hsv = [cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0] for color in colors]
    colors_sorted = [color for _, color in sorted(zip([hsv[2] for hsv in colors_hsv], colors), reverse=True)]
    return colors_sorted


def create_smoother_gradient_background(colors, width, height):
    """Generates a highly blended, grouped-color gradient background with light-to-dark transition."""
    logger.debug("Creating smoother gradient background of dimensions %sx%s", width, height)
    gradient = np.zeros((int(height), int(width), 3), dtype=np.uint8)
    colors_sorted = group_colors_by_lightness(colors)

    if len(colors_sorted) < 2:
        colors_sorted = colors_sorted * 2  # Ensure at least 2 colors for interpolation

    for i in range(int(height)):
        normalized_height = i / height
        primary_color_index = int(normalized_height * (len(colors_sorted) - 1))
        
        if primary_color_index >= len(colors_sorted) - 1:
            primary_color_index = len(colors_sorted) - 2
        
        color_top = np.array(colors_sorted[primary_color_index])
        color_bottom = np.array(colors_sorted[primary_color_index + 1])

        blend_factor_segment = (normalized_height * (len(colors_sorted) - 1)) - primary_color_index
        interpolated_color = (1 - blend_factor_segment) * color_top + blend_factor_segment * color_bottom

        noise_intensity = random.randint(-10, 10)
        mixed_color = np.clip(interpolated_color + noise_intensity, 0, 255)
        gradient[i, :] = mixed_color

    gradient = cv2.GaussianBlur(gradient, (15, 15), 5)
    return gradient


def save_background(image_array, output_path):
    """Saves the generated background image with specified DPI."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    background = Image.fromarray(image_array)
    background.save(output_path, dpi=(350, 350))
    logger.debug("Background saved successfully to: %s", output_path)


def run(state=None):
    """
    Pipeline execution entry point called by artistic_pipeline_magazine.py.
    Enforces strict state validation and No-Default Policy.
    """
    logger.info("Starting generate_background execution.")
    try:
        if not state:
            raise ValueError("❌ NO-DEFAULT POLICY VIOLATION: 'state' object is required for generate_background execution.")
        
        if not hasattr(state, "book_compilation_dir"):
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'state' object lacks 'book_compilation_dir' attribute.")

        image_folder = Path(state.book_compilation_dir)
        output_path = image_folder / "cover_background.jpg"

        if not hasattr(state, "config") or not isinstance(state.config, dict):
            raise KeyError("❌ NO-DEFAULT POLICY VIOLATION: 'state.config' dictionary is missing or invalid.")

        config = state.config.get("generate_background")
        if not config or not isinstance(config, dict):
            raise KeyError("❌ NO-DEFAULT POLICY VIOLATION: 'generate_background' configuration block is missing from config.json.")

        brightness_thresh = config.get("brightness_threshold")
        num_colors = config.get("num_colors_per_image")
        width = config.get("gradient_width")
        height = config.get("gradient_height")
        fallback_colors = config.get("fallback_colors")

        missing = [k for k, v in [
            ("brightness_threshold", brightness_thresh),
            ("num_colors_per_image", num_colors),
            ("gradient_width", width),
            ("gradient_height", height),
            ("fallback_colors", fallback_colors)
        ] if v is None]

        if missing:
            raise ValueError(
                f"❌ NO-DEFAULT POLICY VIOLATION: Required 'generate_background' config fields missing from config.json: {missing}. "
                f"No default values allowed."
            )

        # Process images and extract colors
        unique_colors = process_images(image_folder, num_colors, brightness_thresh)

        # Use config-defined fallback colors if none extracted
        if not unique_colors:
            logger.warning("⚠️ No colors extracted from images. Using config fallback colors.")
            unique_colors = fallback_colors

        # Generate and save background
        background_array = create_smoother_gradient_background(unique_colors, width, height)
        save_background(background_array, output_path)

        logger.info("✅ Background generated successfully and saved as: %s", output_path)

    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        logger.exception("❌ CRITICAL PIPELINE HALT in generate_background: %s", e)
        raise RuntimeError(f"[ERROR] Error generating background: {e}")
