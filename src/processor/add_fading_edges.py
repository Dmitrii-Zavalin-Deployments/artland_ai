import cv2
import numpy as np
import os

def apply_proportional_whitening(input_image_path):
    """
    Places a painting onto a white A4 canvas and applies gradual whitening and blurring
    to the edges with adjusted proportions for top-bottom and left-right effects.
    The central area remains untouched. The final result is saved in the same folder as the input image.

    Parameters:
        input_image_path (str): Path to the artistic painting to process.
    """
    try:
        if not os.path.exists(input_image_path):
            print(f"[ERROR] File not found: '{input_image_path}'")
            return

        # Load the artistic painting
        image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)
        print("[DEBUG] Artistic painting loaded successfully.")

        # Get dimensions of the original painting
        height, width, _ = image.shape

        # Define A4 canvas size (in pixels at 300 DPI)
        a4_width, a4_height = 2480, 3508  # Standard A4 size at 300 DPI
        a4_canvas = np.ones((a4_height, a4_width, 3), dtype=np.uint8) * 255  # White A4 background

        # Resize the painting while maintaining aspect ratio
        scale_factor = min(a4_width / width, a4_height / height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image_resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Calculate position to center the painting on the canvas
        x_offset = (a4_width - new_width) // 2
        y_offset = (a4_height - new_height) // 2

        # Paste the resized painting onto the A4 canvas
        a4_canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = image_resized

        # Create gradient masks for whitening effects
        top_bottom_mask = np.zeros((a4_height, a4_width), dtype=np.float32)
        left_right_mask = np.zeros((a4_height, a4_width), dtype=np.float32)

        # Adjust proportions for top-bottom gradient
        for y in range(a4_height):
            for x in range(a4_width):
                top_bottom_distance = min(y, a4_height - y)
                top_bottom_max_distance = a4_height // 4  # Larger transition zone for top and bottom
                top_bottom_mask[y, x] = max(0, 1 - top_bottom_distance / top_bottom_max_distance)

        # Adjust proportions for left-right gradient
        for y in range(a4_height):
            for x in range(a4_width):
                left_right_distance = min(x, a4_width - x)
                left_right_max_distance = a4_width // 8  # Smaller transition zone for left and right
                left_right_mask[y, x] = max(0, 1 - left_right_distance / left_right_max_distance)

        # Combine top-bottom and left-right masks
        combined_mask = np.maximum(top_bottom_mask, left_right_mask)

        # Apply Gaussian blur to the combined gradient mask to ensure smooth transitions
        combined_mask = cv2.GaussianBlur(combined_mask, (101, 101), 50)

        # Apply the gradient mask to blend the painting's edges into white
        blurred_canvas = cv2.GaussianBlur(a4_canvas, (31, 31), 15)  # Blur for whitening effect
        for c in range(3):  # Apply the mask to each color channel
            a4_canvas[:, :, c] = (a4_canvas[:, :, c] * (1 - combined_mask) + blurred_canvas[:, :, c] * combined_mask).astype(np.uint8)

        # Define the output file path in the same folder as the input image
        output_image_path = os.path.join(os.path.dirname(input_image_path), "proportional_whitened_edges_painting.jpg")

        # Save the final painting with proportional whitening and blurred edges
        cv2.imwrite(output_image_path, a4_canvas)
        print(f"[DEBUG] Final painting with proportional whitened edges saved to: {output_image_path}")

    except Exception as e:
        print(f"[DEBUG] An error occurred: {e}")
        raise RuntimeError(f"[ERROR] Error processing the image: {e}")

if __name__ == "__main__":
    # Define the input image path (previously generated painting)
    input_image_path = "converted_sketches/refined_artistic_painting.jpg"  # Update based on prior script output
    print(f"[DEBUG] Starting proportional whitening and blurring process for: {input_image_path}")

    apply_proportional_whitening(input_image_path)

    print("[DEBUG] Proportional whitening and blurring process completed successfully.")
