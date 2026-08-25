import cv2
from skimage import io
import numpy as np
import os

def refined_artistic_transformation(image_path, output_path):
    """
    Transforms a photo into a vibrant, 3D-like, professional-quality artistic painting.
    Implements enhanced edge preservation, medium-sized object handling, and dynamic contrast
    to ensure a universal, adaptive process suitable for all photo types.

    Parameters:
        image_path (str): Path to the input image.
        output_path (str): Path to save the artistic painting.
    """
    try:
        if not os.path.exists(image_path):
            print(f"[ERROR] File not found: '{image_path}'")
            return

        # Load the original photo
        image = io.imread(image_path)
        print("[DEBUG] Image loaded successfully.")

        # Convert to OpenCV format (BGR)
        image_cv = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # **1. Gradient Preprocessing with Balanced Smoothing**
        print("[DEBUG] Preprocessing gradients to maintain tonal consistency...")
        preprocessed_image = cv2.bilateralFilter(image_cv, d=9, sigmaColor=70, sigmaSpace=70)

        # **2. Edge Preservation for Medium-Sized Objects**
        print("[DEBUG] Refining edges to retain medium-sized elements...")
        edges = cv2.Canny(preprocessed_image, threshold1=100, threshold2=200)
        edges_dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)  # Enhance visibility of edges
        edge_preserved_image = cv2.addWeighted(preprocessed_image, 1, cv2.cvtColor(edges_dilated, cv2.COLOR_GRAY2BGR), 0.3, 0)

        # **3. Dynamic Depth Enhancement for 3D Effect**
        print("[DEBUG] Enhancing shadows and highlights for dimensionality...")
        depth_enhanced_image = cv2.convertScaleAbs(edge_preserved_image, alpha=1.3, beta=20)

        # **4. Adaptive Color Boost**
        print("[DEBUG] Amplifying color vibrancy and contrast...")
        hsv_image = cv2.cvtColor(depth_enhanced_image, cv2.COLOR_BGR2HSV)
        hsv_image[:, :, 1] = cv2.multiply(hsv_image[:, :, 1], 1.30)  # Stronger saturation boost
        hsv_image[:, :, 2] = cv2.multiply(hsv_image[:, :, 2], 1.20)  # Brighter contrast refinement
        color_rich_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        # **5. Refined Stylization**
        print("[DEBUG] Applying artistic brushstroke effects...")
        stylized_image = cv2.stylization(color_rich_image, sigma_s=100, sigma_r=0.3)  # Adjusted parameters for better detail handling

        # **6. Sharpening and Texture Refinement**
        print("[DEBUG] Enhancing sharpness for clarity of medium-sized objects...")
        sharpened_image = cv2.detailEnhance(stylized_image, sigma_s=10, sigma_r=0.1)

        # **7. Selective Noise and Anti-Aliasing**
        print("[DEBUG] Adding selective noise to smooth areas and refining edges...")
        noise = np.random.normal(0, 5, sharpened_image.shape).astype(np.uint8)  # Generate subtle Gaussian noise
        noised_image = cv2.addWeighted(sharpened_image, 0.97, noise, 0.03, 0)  # Light noise blending
        anti_aliased_image = cv2.bilateralFilter(noised_image, d=5, sigmaColor=50, sigmaSpace=50)  # Refine smooth transitions

        # **8. Lighting Simulation for Cohesiveness**
        print("[DEBUG] Simulating realistic lighting effects...")
        lighting_map = cv2.GaussianBlur(anti_aliased_image, (11, 11), 5)  # Fine Gaussian blur
        final_image = cv2.addWeighted(anti_aliased_image, 0.92, lighting_map, 0.08, 0)  # Balanced blending

        # Save the final artistic painting
        print("[DEBUG] Saving the final painting...")
        io.imsave(output_path, cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB))
        print(f"[DEBUG] Final artistic painting saved to: {output_path}")

    except Exception as e:
        print(f"[DEBUG] An error occurred: {e}")
        raise RuntimeError(f"[ERROR] Error processing the image: {e}")

if __name__ == "__main__":
    input_image_path = "original_photos/photo.jpg"  # Path to the input photo
    output_artistic_path = "converted_sketches/refined_artistic_painting.jpg"  # Output path for the final painting

    print(f"[DEBUG] Starting refined artistic transformation: {input_image_path}")
    refined_artistic_transformation(input_image_path, output_artistic_path)
    print("[DEBUG] Refined artistic transformation completed successfully.")



