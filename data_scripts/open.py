import cv2
import os

# paths (update with your dataset folder)
image_folder = "C:\\Users\\Admin\\Desktopkggle\\Ronin_OPEN_DB\\raw images"
label_folder = "C:\\Users\\Admin\\Desktop\\kggle\\Ronin_OPEN_DB\\lbls"

# class names from your data.yaml
class_names = ['Prthenium_hysteroporous','pigweed','jjungle rice']  # <-- replace with your own classes

for img_file in os.listdir(image_folder):
    if img_file.endswith(".jpg") or img_file.endswith(".png"):
        img_path = os.path.join(image_folder, img_file)
        label_path = os.path.join(label_folder, img_file.replace(".jpg", ".txt").replace(".png", ".txt"))
        
        # load image
        img = cv2.imread(img_path)
        h, w, _ = img.shape

        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                for line in f.readlines():
                    cls, x, y, bw, bh = map(float, line.strip().split())
                    cls = int(cls)

                    # convert YOLO format (relative) to pixel coordinates
                    x1 = int((x - bw/2) * w)
                    y1 = int((y - bh/2) * h)
                    x2 = int((x + bw/2) * w)
                    y2 = int((y + bh/2) * h)

                    # draw rectangle + class name
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, class_names[cls], (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 0), 2)

        # show image
        cv2.imshow("Labeled Image", img)
        cv2.waitKey(0)

cv2.destroyAllWindows()
