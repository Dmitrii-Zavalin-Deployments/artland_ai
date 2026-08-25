# src/processor/generate_background.py
import cv2
import numpy as np
import random
from pathlib import Path
from sklearn.cluster import KMeans
from PIL import Image

def extract_colors_from_image(image_path, num_colors, brightness_threshold):
    """Extracts dominant colors from a single image using config parameters."""
    print(f"[INFO] Processing image: {image_path}")
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"[WARNING] Could not read image: {image_path}")
        return []
    
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
            
    print(f"[INFO] Colors extracted from {image_path}: {filtered_colors}")
    return filtered_colors

def process_images(image_folder, num_colors, brightness_threshold):
    """Loops through images, extracts colors, and accumulates unique colors."""
    image_folder = Path(image_folder)
    if not image_folder.exists():
        print(f"[ERROR] Image folder not found: {image_folder}")
        return []

    image_files = sorted(list(image_folder.glob("*.jpg")) + list(image_folder.glob("*.png")))
    if not image_files:
        print("[ERROR] No image files found in the folder!")
        return []

    unique_colors = []
    for image_path in image_files:
        extracted = extract_colors_from_image(image_path, num_colors, brightness_threshold)
        unique_colors.extend(extracted)
        
    print(f"[INFO] Updated unique color list: {unique_colors}")
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
    background = Image.fromarray(image_array)
    background.save(output_path, dpi=(350, 350))


def run(state=None):
    """
    Pipeline execution entry point called by artistic_pipeline_magazine.py.
    """
    image_folder = Path("data/testing-input-output/book_compilation")
    output_path = image_folder / "cover_background.jpg"
    
    config = {}
    if state:
        if hasattr(state, "book_compilation_dir"):
            image_folder = Path(state.book_compilation_dir)
            output_path = image_folder / "cover_background.jpg"
        if hasattr(state, "config") and isinstance(state.config, dict):
            config = state.config.get("generate_background", {})

    # Enforce No-Default Policy
    brightness_thresh = config.get("brightness_threshold")
    num_colors = config.get("num_colors_per_image")
    width = config.get("gradient_width")
    height = config.get("gradient_height")
    fallback_colors = config.get("fallback_colors")

    if any(v is None for v in [brightness_thresh, num_colors, width, height, fallback_colors]):
        raise ValueError("❌ No-Default Policy Error: Required 'generate_background' config fields missing from config.json.")

    # Process images and extract colors
    unique_colors = process_images(image_folder, num_colors, brightness_thresh)

    # Use config-defined fallback colors if none extracted
    if not unique_colors:
        print("[WARNING] No colors extracted from images. Using config fallback colors.")
        unique_colors = fallback_colors

    # Generate and save background
    background_array = create_smoother_gradient_background(unique_colors, width, height)
    save_background(background_array, output_path)

    print(f"[INFO] Background generated successfully and saved as: {output_path}")


if __name__ == "__main__":
    test_config = {
        "brightness_threshold": 50,
        "num_colors_per_image": 5,
        "gradient_width": 800,
        "gradient_height": 1200,
        "fallback_colors": [[255, 200, 220], [200, 220, 255], [220, 255, 200]]
    }
    class MockState:
        book_compilation_dir = "book_compilation"
        config = {"generate_background": test_config}

    run(MockState())
