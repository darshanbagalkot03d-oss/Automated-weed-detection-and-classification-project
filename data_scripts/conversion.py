import os
import xml.etree.ElementTree as ET

# --- Configuration ---
VOC_ANNOTATIONS_DIR = 'C:\\Users\\Admin\\Desktop\\kggle\\Ronin_OPEN_DB\\annotations' # Path to your folder containing XML files
YOLO_OUTPUT_DIR = 'C:\\Users\\Admin\\Desktop\\kggle\\Ronin_OPEN_DB\\lbls'    # Path where you want the .txt files to be saved

# IMPORTANT: Define your class list in the exact order as your labels (0-indexed)
# Example: If 'Jungle_Rice' is class 0, 'Pig_Weed' is class 1, etc.
CLASSES = ['weed'] 

# Create output directory if it doesn't exist
os.makedirs(YOLO_OUTPUT_DIR, exist_ok=True)

# Function to convert the normalized coordinates
def convert(size, box):
    """
    Converts PASCAL VOC bounding box coordinates (xmin, ymax, xmax, ymin)
    to YOLO format (x_center, y_center, width, height) normalized to [0, 1].
    
    size: (image_width, image_height)
    box: (xmin, xmax, ymin, ymax)
    """
    dw = 1. / size[0]
    dh = 1. / size[1]
    
    # Calculate center x and y
    x_center = (box[0] + box[1]) / 2.0
    y_center = (box[2] + box[3]) / 2.0
    
    # Calculate width and height
    w = box[1] - box[0]
    h = box[3] - box[2]
    
    # Normalize and format output (5 decimal places common for precision)
    x_center = round(x_center * dw, 5)
    y_center = round(y_center * dh, 5)
    w = round(w * dw, 5)
    h = round(h * dh, 5)
    
    return (x_center, y_center, w, h)

# Main conversion logic
for filename in os.listdir(VOC_ANNOTATIONS_DIR):
    if not filename.endswith('.xml'):
        continue

    xml_path = os.path.join(VOC_ANNOTATIONS_DIR, filename)
    txt_path = os.path.join(YOLO_OUTPUT_DIR, filename.replace('.xml', '.txt'))

    in_file = open(xml_path, encoding='utf-8')
    out_file = open(txt_path, 'w')
    
    tree = ET.parse(in_file)
    root = tree.getroot()

    # Get image dimensions
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    
    for obj in root.iter('object'):
        cls = obj.find('name').text
        
        if cls not in CLASSES:
            print(f"Warning: Class '{cls}' in {filename} not found in defined CLASSES list. Skipping.")
            continue
            
        # Get class index (0-indexed)
        cls_id = CLASSES.index(cls)
        
        # Get bounding box coordinates
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        
        # Convert to YOLO format
        b = (xmin, xmax, ymin, ymax)
        bb = convert((w, h), b)
        
        # Write to TXT file: [class_id] [x_center] [y_center] [width] [height]
        out_file.write(f"{cls_id} {bb[0]} {bb[1]} {bb[2]} {bb[3]}\n")

    out_file.close()
    in_file.close()

print(f"\n✅ Conversion complete. {len(os.listdir(YOLO_OUTPUT_DIR))} YOLO TXT files created in {YOLO_OUTPUT_DIR}")