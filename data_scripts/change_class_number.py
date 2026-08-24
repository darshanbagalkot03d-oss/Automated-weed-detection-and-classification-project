import os

# Path to pigweed label files
pigweed_labels_path = "Your_floder_path"

# Replace class 0 with 1 for pigweed
for file in os.listdir(pigweed_labels_path):
    if file.endswith(".txt"):
        filepath = os.path.join(pigweed_labels_path, file)
        with open(filepath, "r") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            parts = line.strip().split()
            parts[0] = "4"  # change class id to Pigweed
            new_lines.append(" ".join(parts) + "\n")
        with open(filepath, "w") as f:
            f.writelines(new_lines)