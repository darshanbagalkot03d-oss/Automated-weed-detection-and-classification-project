import cv2
import numpy as np
import os
import random

# --- CONFIGURATION ---
TARGET_CLASS_ID = 2 # Jungle_rice class ID
COPIES_PER_IMAGE = 5 # Number of times to augment each image
# Paths
JUNGLE_RICE_DIR = 'C:\\Users\\Admin\\Desktop\\train\\labels' # Directory containing your 45 Jungle_rice images
ALL_TRAIN_DIR = 'C:\\Users\\Admin\\Desktop\\train' # Directory of all training images (for backgrounds)
OUTPUT_DIR = 'C:\\Users\\Admin\\Desktop\\train' # Output to the same folder to increase dataset size
# ---------------------

def read_yolo_labels(filepath, img_w, img_h):
    # Reads the YOLO .txt file and converts normalized coordinates to pixel coordinates
    # ... Implementation details ...
    pass

def save_yolo_labels(filepath, bboxes, img_w, img_h):
    # Converts pixel coordinates back to normalized YOLO format and saves to .txt
    # ... Implementation details ...
    pass

# 1. Identify all Jungle Rice objects to use as "stencils"
jungle_rice_objects = []
# ... Loop through JUNGLE_RICE_DIR, read labels, and store the crop (stencil) and the class ID ...

# 2. Iterate and Paste
for i in range(COPIES_PER_IMAGE):
    # 3. Select a random background image (ideally one that is not too busy)
    background_path = random.choice(os.listdir(ALL_TRAIN_DIR))
    background_img = cv2.imread(os.path.join(ALL_TRAIN_DIR, background_path))
    
    if background_img is None: continue
    h, w, _ = background_img.shape
    
    # Get existing labels for the background image
    new_bboxes = read_yolo_labels(background_path.replace('.jpg', '.txt'), w, h)
    
    # 4. Select a random Jungle Rice stencil
    stencil_data = random.choice(jungle_rice_objects)
    stencil = stencil_data['crop']
    stencil_h, stencil_w, _ = stencil.shape

    # 5. Determine a random (valid) paste location (x_tl, y_tl)
    # ... Logic to ensure the paste is within bounds and doesn't overlap existing boxes too much ...
    x_paste, y_paste = random.randint(0, w - stencil_w), random.randint(0, h - stencil_h)
    
    # 6. Perform the paste operation
    # background_img[y_paste:y_paste+stencil_h, x_paste:x_paste+stencil_w] = stencil
    # ... Use a mask to paste smoothly ...

    # 7. Add the new bounding box (now in pixel coordinates)
    new_bboxes.append({
        'class_id': 2,
        'x_center': x_paste + stencil_w/2,
        'y_center': y_paste + stencil_h/2,
        'width': stencil_w,
        'height': stencil_h
    })

    # 8. Save the new image and its label file
    new_filename = f"synthetic_jr_{i}_{background_path}"
    # cv2.imwrite(os.path.join(OUTPUT_DIR, new_filename), background_img)
    # save_yolo_labels(os.path.join(OUTPUT_DIR, new_filename.replace('.jpg', '.txt')), new_bboxes, w, h)

# Note: You would likely use a specialized library or tool like Roboflow to perform this complex augmentation safely and efficiently.