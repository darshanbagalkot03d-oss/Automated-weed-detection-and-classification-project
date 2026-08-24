import os
import shutil
from PIL import Image
from imagehash import phash # Removed hex_to_hash as it's not used

# --- Prerequisites ---
# You need to install the required libraries:
# pip install Pillow imagehash

# --- Configuration ---
# 1. Path to your folder containing all the images (original + augmented)
DATASET_PATH = 'C:\\Users\\Admin\\Desktop\\images1'

# 2. Name of the folder where augmented files will be moved for review
REVIEW_FOLDER_NAME = 'C:\\Users\\Admin\\Desktop\\images2'

# 3. Maximum acceptable difference between two image hashes (Hamming Distance).
# A good starting point is 5 or 8.
HASH_TOLERANCE = 8 

# --- Execution ---

def get_image_hash(image_path):
    """Generates a perceptual hash for an image."""
    try:
        # Convert to grayscale ('L') for phash and ensure image is properly loaded
        img = Image.open(image_path).convert('L')
        return phash(img)
    except Exception as e:
        # Print the error but allow the script to continue
        print(f"Error processing {image_path}: {e}")
        return None

# Create the review folder
review_path = os.path.join(DATASET_PATH, REVIEW_FOLDER_NAME)
os.makedirs(review_path, exist_ok=True)
print(f"Review folder created: {review_path}")
print(f"Using HASH_TOLERANCE of: {HASH_TOLERANCE}")

# Dictionary to store hashes: {image_hash_object: [list_of_image_paths]}
# We store the hash object of the FIRST image in the group
hash_groups = {}
moved_count = 0

# Step 1: Group images by perceptual hash
print("\nStep 1: Generating hashes and grouping similar images...")
for filename in os.listdir(DATASET_PATH):
    file_path = os.path.join(DATASET_PATH, filename)
    
    # Skip directories and the review folder
    if not os.path.isfile(file_path) or filename == REVIEW_FOLDER_NAME:
        continue
    # Only check common image files
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    current_hash = get_image_hash(file_path)
    if current_hash is None:
        continue

    # Try to find a similar hash group
    found_group = False
    for existing_hash, paths in hash_groups.items():
        # --- CRITICAL FIX: Use the hash difference/comparison operator ---
        # Hash comparison returns the Hamming distance directly
        hash_difference = current_hash - existing_hash 
        
        if hash_difference <= HASH_TOLERANCE:
            # Append the current image path to the existing group
            hash_groups[existing_hash].append(file_path)
            found_group = True
            break
    
    # If no similar group found, start a new group with the current hash
    if not found_group:
        hash_groups[current_hash] = [file_path]


# Step 2: Identify augmented copies and move them
print("\nStep 2: Identifying and moving augmented copies...")
for hash_key, paths in hash_groups.items():
    if len(paths) > 1:
        # The first image in the list is assumed to be the 'original'
        original_image = paths[0] 
        augmented_copies = paths[1:]
        
        print(f"Found {len(augmented_copies)} copies for: {os.path.basename(original_image)}")
        
        # Move all copies to the review folder
        for copy_path in augmented_copies:
            try:
                shutil.move(copy_path, os.path.join(review_path, os.path.basename(copy_path)))
                moved_count += 1
            except Exception as e:
                print(f"Could not move {copy_path}: {e}")

print("-" * 50)
print(f"✅ Script finished. {moved_count} potential augmented images moved to '{REVIEW_FOLDER_NAME}'.")
print("NEXT STEP: Review the files in the new folder. The remaining images in the main folder are your clean, original set.")