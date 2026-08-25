# src/processor/artistic_painting_processor.py
import cv2
from skimage import io
import numpy as np
import os
from pathlib import Path

def refined_artistic_transformation(image_path, output_path, config=None):
    """
    Transforms a photo into a vibrant, 3D-like, professional-quality artistic painting
    using parameters strictly retrieved from config (No-Default Policy).
    """
    try:
        if not os.path.exists(image_path):
            print(f"[ERROR] File not found: '{image_path}'")
            return

        # Enforce No-Default Policy for configuration parameters
        cfg = config or {}
        if not isinstance(cfg, dict):
            cfg = {}

        bilateral_d = cfg.get("bilateral_d")
        sigma_color = cfg.get("sigma_color")
        sigma_space = cfg.get("sigma_space")
        canny_t1 = cfg.get("canny_threshold1")
        canny_t2 = cfg.get("canny_threshold2")
        depth_alpha = cfg.get("depth_alpha")
        depth_beta = cfg.get("depth_beta")
        sat_mult = cfg.get("saturation_multiplier")
        bright_mult = cfg.get("brightness_multiplier")
        style_s = cfg.get("stylization_sigma_s")
        style_r = cfg.get("stylization_sigma_r")
        detail_s = cfg.get("detail_sigma_s")
        detail_r = cfg.get("detail_sigma_r")

        required_keys = [
            "bilateral_d", "sigma_color", "sigma_space", "canny_threshold1", 
            "canny_threshold2", "depth_alpha", "depth_beta", "saturation_multiplier", 
            "brightness_multiplier", "stylization_sigma_s", "stylization_sigma_r", 
            "detail_sigma_s", "detail_sigma_r"
        ]
        
        missing = [k for k, v in zip(required_keys, [
            bilateral_d, sigma_color, sigma_space, canny_t1, canny_t2, 
            depth_alpha, depth_beta, sat_mult, bright_mult, style_s, 
            style_r, detail_s, detail_r
        ]) if v is None]

        if missing:
            raise ValueError(f"❌ No-Default Policy Error: Required artistic_painting config fields missing from config.json: {missing}")

        # Load the original photo
        image = io.imread(image_path)
        print("[DEBUG] Image loaded successfully for artistic transformation.")

        # Convert to OpenCV format (BGR)
        image_cv = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 1. Gradient Preprocessing with Balanced Smoothing
        print("[DEBUG] Preprocessing gradients to maintain tonal consistency...")
        preprocessed_image = cv2.bilateralFilter(image_cv, d=int(bilateral_d), sigmaColor=float(sigma_color), sigmaSpace=float(sigma_space))

        # 2. Edge Preservation for Medium-Sized Objects
        print("[DEBUG] Refining edges to retain medium-sized elements...")
        edges = cv2.Canny(preprocessed_image, threshold1=int(canny_t1), threshold2=int(canny_t2))
        edges_dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
        edge_preserved_image = cv2.addWeighted(preprocessed_image, 1, cv2.cvtColor(edges_dilated, cv2.COLOR_GRAY2BGR), 0.3, 0)

        # 3. Dynamic Depth Enhancement for 3D Effect
        print("[DEBUG] Enhancing shadows and highlights for dimensionality...")
        depth_enhanced_image = cv2.convertScaleAbs(edge_preserved_image, alpha=float(depth_alpha), beta=float(depth_beta))

        # 4. Adaptive Color Boost
        print("[DEBUG] Amplifying color vibrancy and contrast...")
        hsv_image = cv2.cvtColor(depth_enhanced_image, cv2.COLOR_BGR2HSV)
        hsv_image[:, :, 1] = cv2.multiply(hsv_image[:, :, 1], float(sat_mult))
        hsv_image[:, :, 2] = cv2.multiply(hsv_image[:, :, 2], float(bright_mult))
        color_rich_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        # 5. Refined Stylization
        print("[DEBUG] Applying artistic brushstroke effects...")
        stylized_image = cv2.stylization(color_rich_image, sigma_s=float(style_s), sigma_r=float(style_r))

        # 6. Sharpening and Texture Refinement
        print("[DEBUG] Enhancing sharpness for clarity of medium-sized objects...")
        sharpened_image = cv2.detailEnhance(stylized_image, sigma_s=float(detail_s), sigma_r=float(detail_r))

        # 7. Selective Noise and Anti-Aliasing
        print("[DEBUG] Adding selective noise to smooth areas and refining edges...")
        noise = np.random.normal(0, 5, sharpened_image.shape).astype(np.uint8)
        noised_image = cv2.addWeighted(sharpened_image, 0.97, noise, 0.03, 0)
        anti_aliased_image = cv2.bilateralFilter(noised_image, d=5, sigmaColor=50, sigmaSpace=50)

        # 8. Lighting Simulation for Cohesiveness
        print("[DEBUG] Simulating realistic lighting effects...")
        lighting_map = cv2.GaussianBlur(anti_aliased_image, (11, 11), 5)
        final_image = cv2.addWeighted(anti_aliased_image, 0.92, lighting_map, 0.08, 0)

        # Save the final artistic painting
        print("[DEBUG] Saving the final painting...")
        io.imsave(output_path, cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB))
        print(f"[DEBUG] Final artistic painting saved to: {output_path}")

    except Exception as e:
        print(f"[DEBUG] An error occurred in artistic_painting_processor: {e}")
        raise RuntimeError(f"[ERROR] Error processing the image: {e}")


def run(state=None):
    """
    Pipeline execution entry point called by video and magazine pipelines.
    """
    image_path = "data/testing-input-output/original/photo.jpg"
    config = {}

    if state:
        if hasattr(state, "original_dir"):
            image_path = str(Path(state.original_dir) / "photo.jpg")
        if hasattr(state, "config") and isinstance(state.config, dict):
            config = state.config.get("artistic_painting", {})

    refined_artistic_transformation(image_path, image_path, config=config)


if __name__ == "__main__":
    test_config = {
        "bilateral_d": 9,
        "sigma_color": 70,
        "sigma_space": 70,
        "canny_threshold1": 100,
        "canny_threshold2": 200,
        "depth_alpha": 1.3,
        "depth_beta": 20,
        "saturation_multiplier": 1.30,
        "brightness_multiplier": 1.20,
        "stylization_sigma_s": 100,
        "stylization_sigma_r": 0.3,
        "detail_sigma_s": 10,
        "detail_sigma_r": 0.1
    }
    input_image_path = "original_photos/photo.jpg"
    output_artistic_path = "converted_sketches/refined_artistic_painting.jpg"

    print(f"[DEBUG] Starting refined artistic transformation: {input_image_path}")
    refined_artistic_transformation(input_image_path, output_artistic_path, config=test_config)
    print("[DEBUG] Refined artistic transformation completed successfully.")
