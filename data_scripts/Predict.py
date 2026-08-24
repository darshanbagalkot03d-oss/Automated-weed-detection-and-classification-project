import cv2
import time
from ultralytics import YOLO

# Path to your trained model
MODEL_PATH = "C:\\Users\\Admin\\Documents\\D8055\\6\\MP\\OpenCV_by_PK\\best.pt"   # change if file is in another folder

# Load the trained model
model = YOLO(MODEL_PATH)

# Class names (automatically loaded from training config)
class_names = model.names

# Open webcam
cap = cv2.VideoCapture(0)  # 0 = default webcam
if not cap.isOpened():
    raise SystemExit("ERROR: Could not open webcam")

prev_time = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Failed to grab frame")
        break

    # Run detection
    results = model(frame, imgsz=640, conf=0.35)

    # Get annotated frame
    annotated = results[0].plot()

    # Show FPS
    cur_time = time.time()
    fps = 1 / (cur_time - prev_time) if prev_time else 0
    prev_time = cur_time
    cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Display output
    cv2.imshow("Weed Detector", annotated)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
