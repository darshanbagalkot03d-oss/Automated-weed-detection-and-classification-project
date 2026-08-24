import os

# --- Configuration (MUST MATCH your data.yaml) ---
# Map Class ID (0, 1, 2) to Class Name
CLASS_NAMES = {
    0: "Prthenium_hysteroporous",
    1: "pigweed",
    2: "jungle_rice"
}
# --- IMPORTANT: Change this path before each run! ---
LABELS_DIR = 'Your_folder_path' 
# ---------------------------------------------------

class_counts = {name: 0 for name in CLASS_NAMES.values()}
total_annotations = 0

print(f"--- Starting annotation count in: {LABELS_DIR} ---")

for filename in os.listdir(LABELS_DIR):
    if filename.endswith('.txt'):
        label_path = os.path.join(LABELS_DIR, filename)
        
        try:
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts and len(parts) >= 5:
                        # The first element is the class ID
                        class_id = int(parts[0])
                        
                        if class_id in CLASS_NAMES:
                            class_counts[CLASS_NAMES[class_id]] += 1
                            total_annotations += 1
        except Exception as e:
            print(f"Error reading {filename}: {e}")

print("\n--- Final Annotation Count (Bounding Boxes) ---")
print(f"Total Bounding Boxes: {total_annotations:,}")

if total_annotations > 0:
    for name, count in class_counts.items():
        percentage = (count / total_annotations) * 100
        print(f"  - {name}: {count:,} ({percentage:.1f}%)")
else:
    print("No annotations found. Check your LABELS_DIR path.")