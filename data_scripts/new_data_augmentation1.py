import cv2
import numpy as np
import os
import random

# --- CONFIGURATION (UPDATE THESE PATHS) ---
# NOTE: Use forward slashes (/) or double backslashes (\\) for Windows paths
TARGET_CLASS_ID = 1  # Jungle_rice class ID (based on your data.yaml names index)
COPIES_PER_IMAGE = 5 # Number of augmented images to generate for each original Jungle_rice image.
                     # Setting this to 5 will result in many new images.

# Directories relative to where you run the script (e.g., project root)
# Ensure these directories are correct and contain your images and labels.
IMAGES_DIR = 'C:\\Users\\Admin\\Desktop\\pweed\\images'
LABELS_DIR = 'C:\\Users\\Admin\\Desktop\\pweed\\labels'
OUTPUT_DIR = 'C:\\Users\\Admin\\Desktop\\pweed\\images' # Changed for better organization
OUTPUT_LABELS_DIR = 'C:\\Users\\Admin\\Desktop\\pweed\\labels' # Changed for better organization
# ------------------------------------------

# --- UTILITY FUNCTIONS (UNCHANGED) ---

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
    
    for label_file in os.listdir(LABELS_DIR):
        if not label_file.endswith('.txt'): continue
            
        label_path = os.path.join(LABELS_DIR, label_file)
        img_file = label_file.replace('.txt', '.jpg')
        img_path = os.path.join(IMAGES_DIR, img_file)
        
        if not os.path.exists(img_path): continue

        img = cv2.imread(img_path)
        if img is None: continue
            
        h, w, _ = img.shape
        bboxes = read_yolo_labels(label_path, w, h)
        
        for bbox in bboxes:
            if bbox['class_id'] == TARGET_CLASS_ID:
                # Crop the object (stencil)
                stencil = img[bbox['y_tl']:bbox['y_tl'] + bbox['h'], 
                              bbox['x_tl']:bbox['x_tl'] + bbox['w']]
                
                if stencil.size > 0:
                    stencils.append({
                        'stencil': stencil,
                        'w': bbox['w'],
                        'h': bbox['h']
                    })
    
    print(f"Extracted {len(stencils)} Jungle Rice stencils for augmentation.")
    return stencils

# --- NEW AUGMENTATION FUNCTION ---
def transform_stencil(stencil):
    """Applies random geometric and color transformations to a stencil."""
    h_s, w_s, _ = stencil.shape
    
    # 1. Random Flip
    if random.random() < 0.5:
        stencil = cv2.flip(stencil, 1) # Horizontal flip
        
    # 2. Random Scale (0.8x to 1.2x)
    scale_factor = random.uniform(0.8, 1.2)
    new_w = int(w_s * scale_factor)
    new_h = int(h_s * scale_factor)
    
    # Resizing ensures the new bounding box dimensions are correct
    stencil = cv2.resize(stencil, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    w_s, h_s = new_w, new_h # Update dimensions
    
    # 3. Random Color Jitter (HSV)
    stencil_hsv = cv2.cvtColor(stencil, cv2.COLOR_BGR2HSV)
    
    # Apply small random shifts
    h_shift = random.randint(-5, 5)
    s_factor = random.uniform(0.9, 1.1)
    v_factor = random.uniform(0.8, 1.2)
    
    # --- FIX implemented below: Convert to int16 before arithmetic ---
    
    # Hue Channel (0-180 range in OpenCV)
    hue_channel = stencil_hsv[:, :, 0].astype(np.int16) # Convert to signed integer
    hue_channel += h_shift # Perform addition safely
    # Clip and convert back to uint8
    stencil_hsv[:, :, 0] = np.clip(hue_channel, 0, 180).astype(np.uint8) 
    
    # Saturation and Value Channels (0-255 range)
    # The clip logic should also be applied to S and V channels for safety if factors are used
    sat_channel = stencil_hsv[:, :, 1].astype(np.float32) * s_factor
    val_channel = stencil_hsv[:, :, 2].astype(np.float32) * v_factor

    stencil_hsv[:, :, 1] = np.clip(sat_channel, 0, 255).astype(np.uint8)
    stencil_hsv[:, :, 2] = np.clip(val_channel, 0, 255).astype(np.uint8)
    # --- End FIX ---
    
    stencil = cv2.cvtColor(stencil_hsv, cv2.COLOR_HSV2BGR)
    
    return stencil, w_s, h_s
# def transform_stencil(stencil):
    # """Applies random geometric and color transformations to a stencil."""
    # h_s, w_s, _ = stencil.shape
    # 
    # 1. Random Flip
    # if random.random() < 0.5:
        # stencil = cv2.flip(stencil, 1) # Horizontal flip
        # 
    # 2. Random Scale (0.8x to 1.2x)
    # scale_factor = random.uniform(0.8, 1.2)
    # new_w = int(w_s * scale_factor)
    # new_h = int(h_s * scale_factor)
    # 
    # Resizing ensures the new bounding box dimensions are correct
    # stencil = cv2.resize(stencil, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    # w_s, h_s = new_w, new_h # Update dimensions
    # 
    # 3. Random Color Jitter (HSV)
    # stencil_hsv = cv2.cvtColor(stencil, cv2.COLOR_BGR2HSV)
    # 
    # Apply small random shifts
    # h_shift = random.randint(-5, 5)
    # s_factor = random.uniform(0.9, 1.1)
    # v_factor = random.uniform(0.8, 1.2)
    # 
    # stencil_hsv[:, :, 0] = np.clip(stencil_hsv[:, :, 0] + h_shift, 0, 180) # Hue (0-180 range)
    # stencil_hsv[:, :, 1] = np.clip(stencil_hsv[:, :, 1] * s_factor, 0, 255) # Saturation
    # stencil_hsv[:, :, 2] = np.clip(stencil_hsv[:, :, 2] * v_factor, 0, 255) # Value
    # 
    # stencil = cv2.cvtColor(stencil_hsv, cv2.COLOR_HSV2BGR)
    # 
    # return stencil, w_s, h_s

# --- MAIN AUGMENTATION LOGIC ---

# Create output directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_LABELS_DIR, exist_ok=True)

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
        background_path = random.choice(background_images)
        
        # Load stencil and apply transformations
        stencil, stencil_w, stencil_h = transform_stencil(stencil_data['stencil'].copy())
        
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
        
        # 5. Determine a random (VALID AND CONSTRAINED) paste location (x_tl, y_tl)
        
        # Constrain vertical placement: Jungle Rice should appear in the lower 70% of the image (ground)
        y_min_constraint = int(0.3 * h_bg) 
        y_max_paste = h_bg - stencil_h
        # --- FIX: Check for empty Y range before calling random.randint ---
        if y_min_constraint >= y_max_paste:
    # This stencil is too tall to fit in the lower 70% of this background. Skip it.
             continue
        # Ensure x_paste and y_paste stay within bounds
        x_paste = random.randint(0, w_bg - stencil_w)
        y_paste = random.randint(y_min_constraint, h_bg - stencil_h)
        
        # 6. Perform SEAMLESS CLONING
        
        # Create a mask for the stencil (full white rectangle for now, but better if it was a segmentation mask)
        mask = 255 * np.ones(stencil.shape, stencil.dtype)
        
        # Define the center point of the paste area
        center_x = x_paste + stencil_w // 2
        center_y = y_paste + stencil_h // 2
        center = (center_x, center_y)
        
        # Use NORMAL_CLONE for better texture preservation
        try:
            background_img = cv2.seamlessClone(stencil, background_img, mask, center, cv2.NORMAL_CLONE)
        except Exception as e:
            # Handle cases where seamlessClone fails (e.g., stencil too close to edge)
            # Fallback to simple paste if necessary, or just skip
            # print(f"Seamless clone failed: {e}. Skipping this instance.")
            continue
        
        # 7. Add the new bounding box (now in pixel coordinates)
        new_bboxes.append({
            'class_id': TARGET_CLASS_ID,
            'x_tl': x_paste,
            'y_tl': y_paste,
            'w': stencil_w,
            'h': stencil_h
        })

        # 8. Save the new image and its label file
        
        # Use a unique name
        base_name, ext = os.path.splitext(background_path)
        new_filename_base = f"JR_AUG_{i}_{base_name}"
        
        cv2.imwrite(os.path.join(OUTPUT_DIR, new_filename_base + ext), background_img)
        save_yolo_labels(os.path.join(OUTPUT_LABELS_DIR, new_filename_base + '.txt'), new_bboxes, w_bg, h_bg)
        
        new_files_count += 1

    print(f"\n--- Augmentation Complete ---")
    print(f"Successfully generated {new_files_count} new image-label pairs.")
    print(f"Output images in: {OUTPUT_DIR}")
    print(f"Output labels in: {OUTPUT_LABELS_DIR}")
    print(f"Remember to update your YOLO configuration (data.yaml) to include these new folders in your training set.")