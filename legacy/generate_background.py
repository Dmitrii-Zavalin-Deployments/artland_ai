import os
import cv2
import numpy as np
import random
from glob import glob
from sklearn.cluster import KMeans
from PIL import Image

# Path to the folder containing images
IMAGE_FOLDER = "book_compilation"
OUTPUT_IMAGE = os.path.join(IMAGE_FOLDER, "background.jpg")

# Parameters for filtering dark colors
BRIGHTNESS_THRESHOLD = 50  # HSV V-channel threshold
NUM_COLORS_PER_IMAGE = 5   # Reduced number of clusters per image for efficiency

# Global list to store extracted colors
unique_colors = []

def extract_colors_from_image(image_path):
    """Extracts dominant colors from a single image."""
    print(f"[INFO] Processing image: {image_path}") # Log start
    image = cv2.imread(image_path)
    if image is None:
        print(f"[WARNING] Could not read image: {image_path}")
        return []
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    reshaped_image = image.reshape(-1, 3)

    # Use KMeans to find dominant colors
    kmeans = KMeans(n_clusters=NUM_COLORS_PER_IMAGE, random_state=42, n_init=10)
    kmeans.fit(reshaped_image)
    colors = kmeans.cluster_centers_.astype(int)

    # Filter and store light colors
    filtered_colors = []
    for color in colors:
        hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
        if hsv[2] > BRIGHTNESS_THRESHOLD:  # V-channel brightness check
            filtered_colors.append(color.tolist())
    print(f"[INFO] Colors extracted from {image_path}: {filtered_colors}")
    return filtered_colors

def process_images(image_folder):
    """Loops through images, extracts colors, and accumulates unique colors."""
    image_files = glob(os.path.join(image_folder, "*.jpg"))
    if not image_files:
        print("[ERROR] No .jpg images found in the folder!")
        return
    for image_path in image_files:
        extracted_colors = extract_colors_from_image(image_path)
        unique_colors.extend(extracted_colors) # Add new extracted colors
    # Log the updated unique color list
    print(f"[INFO] Updated unique color list: {unique_colors}")

def group_colors_by_lightness(colors):
    """Reorders colors so lighter shades move toward the top and darker ones toward the bottom."""
    if not colors:
        return colors
    # Convert to HSV for better sorting by brightness (V channel)
    colors_hsv = [cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0] for color in colors]
    # Sort colors by brightness (lightest to darkest)
    colors_sorted = [color for _, color in sorted(zip([hsv[2] for hsv in colors_hsv], colors), reverse=True)]
    return colors_sorted

def create_smoother_gradient_background(colors, width=800, height=1200):
    """Generates a highly blended, grouped-color gradient background with light-to-dark transition."""
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    colors_sorted = group_colors_by_lightness(colors) # Ensure lighter colors are at the top

    for i in range(height):
        # Determine the position along the height (0 to 1)
        normalized_height = i / height

        # Calculate the index for the primary color.
        # This makes sure we transition through the sorted colors.
        # The `int` cast ensures an integer index.
        primary_color_index = int(normalized_height * (len(colors_sorted) - 1))
        
        # Ensure the index doesn't go out of bounds for the last color
        if primary_color_index >= len(colors_sorted) - 1:
            primary_color_index = len(colors_sorted) - 2 # Use the second to last for blending with last
        
        # Get the two colors to blend between for this row
        color_top = np.array(colors_sorted[primary_color_index])
        color_bottom = np.array(colors_sorted[primary_color_index + 1])

        # Calculate the blend factor based on the fractional part of normalized_height
        # This creates a smooth transition between `color_top` and `color_bottom`
        blend_factor_segment = (normalized_height * (len(colors_sorted) - 1)) - primary_color_index
        
        # Linearly interpolate between color_top and color_bottom
        interpolated_color = (1 - blend_factor_segment) * color_top + blend_factor_segment * color_bottom

        # Introduce subtle variations to reduce abrupt shifts
        noise_intensity = random.randint(-10, 10)
        mixed_color = np.clip(interpolated_color + noise_intensity, 0, 255)
        
        gradient[i, :] = mixed_color

    # Apply directional blur to soften edges
    gradient = cv2.GaussianBlur(gradient, (15, 15), 5) # Increased blur strength for smoother transitions
    return gradient

def save_background(image_array, output_path):
    """Saves the generated background image with specified DPI."""
    background = Image.fromarray(image_array)
    # Set the DPI to 350 for high-quality printing
    background.save(output_path, dpi=(350, 350))

# Process images sequentially, accumulating colors
process_images(IMAGE_FOLDER)

# If no colors extracted, set default light colors
if not unique_colors:
    unique_colors = [[255, 200, 220], [200, 220, 255], [220, 255, 200]] # Light pastel tones

# Generate the grouped, blended, and repositioned background
background_array = create_smoother_gradient_background(unique_colors)

# Save the background image
save_background(background_array, OUTPUT_IMAGE)

print(f"[INFO] Background generated with **light-to-dark gradient positioning, softened edges, enhanced blur strength, and 350 DPI** and saved as: {OUTPUT_IMAGE}")


