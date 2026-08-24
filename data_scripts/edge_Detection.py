import cv2
import numpy as np
from ultralytics import YOLO

# --- CONFIGURATION (UPDATE THESE PATHS) ---
# NOTE: Use the path to your best model weights (e.g., from runs/detect/train/weights/best.pt)
MODEL_PATH = '/path/to/your/best.pt'
INPUT_IMAGE_PATH = '49.jpg' 
OUTPUT_IMAGE_PATH = '49_parthenium_edge_analysis.jpg'

# 0 is the class ID for 'Prthenium_hysteroporous' based on your data.yaml
TARGET_CLASS_ID = 0 

# Canny Edge Detection Parameters
CANNY_LOWER_THRESH = 50
CANNY_UPPER_THRESH = 150
# ------------------------------------------

def apply_canny_to_crop(image, box_coords):
    """Crops the image based on YOLO box, applies Canny, and returns the edge map."""
    
    # 1. Unpack coordinates (x_min, y_min, x_max, y_max) and ensure they are integers
    x1, y1, x2, y2 = map(int, box_coords)

    # 2. Crop the detected object
    weed_crop = image[y1:y2, x1:x2]

    if weed_crop.size == 0:
        return None

    # 3. Pre-process for Canny
    gray_crop = cv2.cvtColor(weed_crop, cv2.COLOR_BGR2GRAY)
    blurred_crop = cv2.GaussianBlur(gray_crop, (5, 5), 0)

    # 4. Apply Canny Edge Detector
    edges = cv2.Canny(blurred_crop, CANNY_LOWER_THRESH, CANNY_UPPER_THRESH)

    # 5. Convert edge map back to color (3 channels) so it can be overlaid on the original image
    edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Optional: Highlight edges in red for demonstration
    edges_color[np.where((edges_color == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

    return edges_color


def run_yolo_and_edge_detection():
    """Performs YOLO prediction and then applies Canny Edge Detection to each target detection."""
    
    # Load your trained model
    model = YOLO(MODEL_PATH)

    # Run prediction (use a low confidence threshold to capture a detection)
    results = model(INPUT_IMAGE_PATH, conf=0.10, iou=0.5, verbose=False)
    
    # Load the original image for drawing
    original_img = cv2.imread(INPUT_IMAGE_PATH)
    if original_img is None:
        print(f"Error: Could not load image {INPUT_IMAGE_PATH}")
        return

    # Process each detection
    for r in results:
        # Check if detections were found
        if r.boxes.xyxy.numel() == 0:
            print("No objects detected. Try lowering the 'conf' threshold in the model() call.")
            continue

        # Iterate through all detected boxes
        for box in r.boxes:
            class_id = int(box.cls)
            
            # Only process the target weed class (Parthenium)
            if class_id == TARGET_CLASS_ID:
                box_coords = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(int, box_coords)

                # Get the Canny Edge Map for the cropped area
                edge_map_color = apply_canny_to_crop(original_img, box_coords)

                if edge_map_color is not None:
                    # Resize the edge map back to the size of the bounding box
                    # This ensures the dimensions match for the overlay
                    edge_h, edge_w = edge_map_color.shape[:2]

                    # Overlay the edge map onto the original image within the bounding box
                    original_img[y1:y2, x1:x2] = edge_map_color
                    
                    # Draw a final bounding box around the whole region for clarity
                    cv2.rectangle(original_img, (x1, y1), (x2, y2), (255, 0, 0), 2) # Blue box

    # Save the final result
    cv2.imwrite(OUTPUT_IMAGE_PATH, original_img)
    print(f"\nDemonstration complete. Output saved to: {OUTPUT_IMAGE_PATH}")
    print(f"Look for the blue bounding box containing the edge map of the detected Parthenium.")

if __name__ == '__main__':
    run_yolo_and_edge_detection()