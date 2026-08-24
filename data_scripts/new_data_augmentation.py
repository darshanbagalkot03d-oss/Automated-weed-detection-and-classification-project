import cv2
import numpy as np
import os
import random

# --- CONFIGURATION (UPDATE THESE PATHS) ---
# NOTE: Use forward slashes (/) or double backslashes (\\) for Windows paths
TARGET_CLASS_ID = 2  # Jungle_rice class ID (based on your data.yaml names index)
COPIES_PER_IMAGE = 5 # Number of augmented images to generate for each original Jungle_rice image.
                     # Setting this to 5 will result in ~225 new images (45 original * 5 copies).

# Directories relative to where you run the script (e.g., project root)
IMAGES_DIR = 'C:\\Users\\Admin\\Desktop\\junglerice'   # Directory for ALL training images (as backgrounds)
LABELS_DIR = 'C:\\Users\\Admin\\Desktop\\junglerice\\labels'   # Directory for ALL training labels
OUTPUT_DIR = 'C:\\Users\\Admin\\Desktop\\junglerice'   # Output images to the same folder
OUTPUT_LABELS_DIR = 'C:\\Users\\Admin\\Desktop\\junglerice\\labels' # Output labels to the same folder
# ------------------------------------------

def read_yolo_labels(label_path, img_w, img_h):
    """Reads a YOLO .txt label file and returns bounding boxes in pixel coordinates."""
    bboxes = []
    if not os.path.exists(label_path):
        return bboxes
        
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                class_id = int(parts[0])
                # Normalized coordinates
                x_center_norm, y_center_norm, w_norm, h_norm = map(float, parts[1:])
                
                # Convert to pixel coordinates (x_tl, y_tl, w, h)
                w_px = w_norm * img_w
                h_px = h_norm * img_h
                x_tl_px = (x_center_norm * img_w) - (w_px / 2)
                y_tl_px = (y_center_norm * img_h) - (h_px / 2)
                
                bboxes.append({
                    'class_id': class_id,
                    'x_tl': int(x_tl_px), 
                    'y_tl': int(y_tl_px), 
                    'w': int(w_px), 
                    'h': int(h_px)
                })
    return bboxes

def save_yolo_labels(label_path, bboxes, img_w, img_h):
    """Saves bounding boxes to a YOLO .txt label file in normalized coordinates."""
    with open(label_path, 'w') as f:
        for bbox in bboxes:
            # Convert pixel coordinates (x_tl, y_tl, w, h) back to normalized (x_c, y_c, w, h)
            x_center_norm = (bbox['x_tl'] + bbox['w'] / 2) / img_w
            y_center_norm = (bbox['y_tl'] + bbox['h'] / 2) / img_h
            w_norm = bbox['w'] / img_w
            h_norm = bbox['h'] / img_h
            
            # Write line: class_id x_c y_c w h
            f.write(f"{bbox['class_id']} {x_center_norm:.6f} {y_center_norm:.6f} {w_norm:.6f} {h_norm:.6f}\n")

def get_jungle_rice_stencils():
    """Extracts all Jungle_rice objects and their image patches (stencils) from the dataset."""
    stencils = []
    
    # 1. Iterate through all label files
    for label_file in os.listdir(LABELS_DIR):
        if not label_file.endswith('.txt'):
            continue
            
        label_path = os.path.join(LABELS_DIR, label_file)
        img_file = label_file.replace('.txt', '.jpg') # Assuming images are .jpg
        img_path = os.path.join(IMAGES_DIR, img_file)
        
        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue
            
        h, w, _ = img.shape
        bboxes = read_yolo_labels(label_path, w, h)
        
        # 2. Extract stencils only for the TARGET_CLASS_ID
        for bbox in bboxes:
            if bbox['class_id'] == TARGET_CLASS_ID:
                # Crop the object (stencil)
                stencil = img[bbox['y_tl']:bbox['y_tl'] + bbox['h'], 
                              bbox['x_tl']:bbox['x_tl'] + bbox['w']]
                
                # Check for empty stencil (should not happen if bboxes are valid)
                if stencil.size > 0:
                    stencils.append({
                        'stencil': stencil,
                        'w': bbox['w'],
                        'h': bbox['h']
                    })
    
    print(f"Extracted {len(stencils)} Jungle Rice stencils for augmentation.")
    return stencils

# --- MAIN AUGMENTATION LOGIC ---

# 1. Extract all stencils once
jungle_rice_stencils = get_jungle_rice_stencils()

if not jungle_rice_stencils:
    print("ERROR: No Jungle Rice stencils found. Check TARGET_CLASS_ID and paths.")
else:
    print(f"Starting Copy-Paste Augmentation, generating {len(jungle_rice_stencils) * COPIES_PER_IMAGE} new annotations...")
    
    # 2. Get a list of all images to use as backgrounds
    background_images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.png'))]
    
    # Counter for new files
    new_files_count = 0
    
    for i in range(len(jungle_rice_stencils) * COPIES_PER_IMAGE):
        
        # 3. Select random stencil and background
        stencil_data = random.choice(jungle_rice_stencils)
        stencil = stencil_data['stencil']
        stencil_w, stencil_h = stencil_data['w'], stencil_data['h']
        
        background_path = random.choice(background_images)
        background_img = cv2.imread(os.path.join(IMAGES_DIR, background_path))
        
        if background_img is None: continue
        
        h_bg, w_bg, _ = background_img.shape
        
        # Skip if stencil is too large for the background
        if stencil_w >= w_bg or stencil_h >= h_bg: continue
        
        # 4. Get existing labels for the background image
        label_filename = background_path.rsplit('.', 1)[0] + '.txt'
        label_path = os.path.join(LABELS_DIR, label_filename)
        
        # Get existing bboxes (in pixel coordinates)
        existing_bboxes = read_yolo_labels(label_path, w_bg, h_bg)
        new_bboxes = existing_bboxes.copy()
        
        # 5. Determine a random (valid) paste location (x_tl, y_tl)
        # Randomly choose top-left corner
        x_paste = random.randint(0, w_bg - stencil_w)
        y_paste = random.randint(0, h_bg - stencil_h)
        
        # 6. Perform the paste operation
        # NOTE: A simple paste (like this) works best when objects are roughly segmented.
        background_img[y_paste:y_paste + stencil_h, x_paste:x_paste + stencil_w] = stencil
        
        # 7. Add the new bounding box (now in pixel coordinates)
        new_bboxes.append({
            'class_id': TARGET_CLASS_ID,
            'x_tl': x_paste,
            'y_tl': y_paste,
            'w': stencil_w,
            'h': stencil_h
        })

        # 8. Save the new image and its label file
        # Use a unique name to avoid overwriting original files
        new_filename_base = f"JR_AUG_{i}_{background_path}"
        
        cv2.imwrite(os.path.join(OUTPUT_DIR, new_filename_base), background_img)
        save_yolo_labels(os.path.join(OUTPUT_LABELS_DIR, new_filename_base.replace('.jpg', '.txt')), new_bboxes, w_bg, h_bg)
        
        new_files_count += 1

    print(f"\n--- Augmentation Complete ---")
    print(f"Successfully generated {new_files_count} new image-label pairs in {OUTPUT_DIR} and {OUTPUT_LABELS_DIR}")
    print(f"You should now run your training command again.")