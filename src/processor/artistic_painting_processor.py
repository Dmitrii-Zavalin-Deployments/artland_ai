# src/processor/artistic_painting_processor.py
import logging
from pathlib import Path

import cv2
import numpy as np
from skimage import io

logger = logging.getLogger(__name__)


def refined_artistic_transformation(image_path, output_path, config):
    """
    Transforms a photo into a vibrant, 3D-like, professional-quality artistic painting
    using parameters strictly retrieved from config (No-Default Policy).
    """
    image_path = Path(image_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Input image for artistic transformation not found at '{image_path}'."
        )

    # Enforce No-Default Policy for configuration parameters
    if not isinstance(config, dict):
        raise TypeError("❌ NO-DEFAULT POLICY VIOLATION: 'config' must be a valid dictionary.")

    bilateral_d = config.get("bilateral_d")
    sigma_color = config.get("sigma_color")
    sigma_space = config.get("sigma_space")
    canny_t1 = config.get("canny_threshold1")
    canny_t2 = config.get("canny_threshold2")
    depth_alpha = config.get("depth_alpha")
    depth_beta = config.get("depth_beta")
    sat_mult = config.get("saturation_multiplier")
    bright_mult = config.get("brightness_multiplier")
    style_s = config.get("stylization_sigma_s")
    style_r = config.get("stylization_sigma_r")
    detail_s = config.get("detail_sigma_s")
    detail_r = config.get("detail_sigma_r")

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
        raise ValueError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Required 'artistic_painting' config fields missing from config.json: {missing}. "
            f"No default values allowed."
        )

    # Load the original photo
    image = io.imread(str(image_path))
    logger.info("✅ Image loaded successfully for artistic transformation.")

    # Convert to OpenCV format (BGR)
    image_cv = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # 1. Gradient Preprocessing with Balanced Smoothing
    logger.debug("Preprocessing gradients to maintain tonal consistency...")
    preprocessed_image = cv2.bilateralFilter(image_cv, d=int(bilateral_d), sigmaColor=float(sigma_color), sigmaSpace=float(sigma_space))

    # 2. Edge Preservation for Medium-Sized Objects
    logger.debug("Refining edges to retain medium-sized elements...")
    edges = cv2.Canny(preprocessed_image, threshold1=int(canny_t1), threshold2=int(canny_t2))
    edges_dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
    edge_preserved_image = cv2.addWeighted(preprocessed_image, 1, cv2.cvtColor(edges_dilated, cv2.COLOR_GRAY2BGR), 0.3, 0)

    # 3. Dynamic Depth Enhancement for 3D Effect
    logger.debug("Enhancing shadows and highlights for dimensionality...")
    depth_enhanced_image = cv2.convertScaleAbs(edge_preserved_image, alpha=float(depth_alpha), beta=float(depth_beta))

    # 4. Adaptive Color Boost
    logger.debug("Amplifying color vibrancy and contrast...")
    hsv_image = cv2.cvtColor(depth_enhanced_image, cv2.COLOR_BGR2HSV)
    hsv_image[:, :, 1] = cv2.multiply(hsv_image[:, :, 1], float(sat_mult))
    hsv_image[:, :, 2] = cv2.multiply(hsv_image[:, :, 2], float(bright_mult))
    color_rich_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    # 5. Refined Stylization
    logger.debug("Applying artistic brushstroke effects...")
    stylized_image = cv2.stylization(color_rich_image, sigma_s=float(style_s), sigma_r=float(style_r))

    # 6. Sharpening and Texture Refinement
    logger.debug("Enhancing sharpness for clarity of medium-sized objects...")
    sharpened_image = cv2.detailEnhance(stylized_image, sigma_s=float(detail_s), sigma_r=float(detail_r))

    # 7. Selective Noise and Anti-Aliasing
    logger.debug("Adding selective noise to smooth areas and refining edges...")
    noise = np.random.normal(0, 5, sharpened_image.shape).astype(np.uint8)
    noised_image = cv2.addWeighted(sharpened_image, 0.97, noise, 0.03, 0)
    anti_aliased_image = cv2.bilateralFilter(noised_image, d=5, sigmaColor=50, sigmaSpace=50)

    # 8. Lighting Simulation for Cohesiveness
    logger.debug("Simulating realistic lighting effects...")
    lighting_map = cv2.GaussianBlur(anti_aliased_image, (11, 11), 5)
    final_image = cv2.addWeighted(anti_aliased_image, 0.92, lighting_map, 0.08, 0)

    # Save the final artistic painting
    output_path.parent.mkdir(parents=True, exist_ok=True)
    io.imsave(str(output_path), cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB))
    logger.info("✅ Final artistic painting saved to: %s", output_path)


def run(state=None):
    """
    Pipeline execution entry point called by video and magazine pipelines.
    Enforces strict state validation.
    """
    logger.info("Starting artistic_painting_processor execution.")
    try:
        if not state:
            raise ValueError("❌ NO-DEFAULT POLICY VIOLATION: 'state' object is required for artistic_painting_processor execution.")
        
        if not hasattr(state, "current_frame_path") or not state.current_frame_path:
            raise AttributeError("❌ NO-DEFAULT POLICY VIOLATION: 'state' object lacks 'current_frame_path' attribute or it is empty.")
        
        image_path = Path(state.current_frame_path)

        if not hasattr(state, "config") or not isinstance(state.config, dict):
            raise KeyError("❌ NO-DEFAULT POLICY VIOLATION: 'state.config' dictionary is missing or invalid.")
        
        config = state.config.get("artistic_painting")
        if not config:
            raise KeyError("❌ NO-DEFAULT POLICY VIOLATION: 'artistic_painting' configuration block is missing from config.json.")

        refined_artistic_transformation(image_path, image_path, config=config)
        logger.info("artistic_painting_processor execution completed successfully.")

    except (OSError, ValueError, TypeError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        logger.exception("❌ CRITICAL PIPELINE HALT in artistic_painting_processor")
        raise RuntimeError(f"[ERROR] Error processing the image: {e}")
