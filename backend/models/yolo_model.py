# yolo_model.py
import os
import io
from ultralytics import YOLO
from PIL import Image
import numpy as np

class YOLO_Model:
    def __init__(self, model_path):
        """Initializes the YOLO model from a given path."""
        # Using the ultralytics YOLO class
        self.model = YOLO(model_path)
        self.names = self.model.names
        print(f"YOLO model initialized and class names loaded.")

    def predict(self, image_data):
        """
        Performs detection on image data (bytes).
        
        Args:
            image_data (bytes): The raw image data (e.g., from an uploaded file or camera stream).
            
        Returns:
            tuple: (detection_results, annotated_pil_image)
            - detection_results (dict): Structured detection data.
            - annotated_pil_image (PIL.Image): The image with bounding boxes drawn.
        """
        
        # 1. Load the image from bytes using PIL
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # 2. Run the model prediction
        # conf=0.25 is a common default confidence threshold
        results = self.model.predict(source=image, save=False, save_txt=False, verbose=False, conf=0.25) 

        if not results:
            return {'detections': [], 'count': 0}, image

        result = results[0]
        
        # 3. Process the raw results into a clean dictionary format
        detections_list = []
        
        if result.boxes:
            for box in result.boxes:
                # Bounding box coordinates in pixels: [xmin, ymin, xmax, ymax]
                # Convert to integer list for cleaner JSON/DB storage
                xyxy = box.xyxy[0].cpu().numpy().astype(int).tolist()
                confidence = box.conf[0].cpu().item()
                class_id = int(box.cls[0].cpu().item())
                
                detections_list.append({
                    'name': self.names.get(class_id, 'Unknown'),
                    'confidence': confidence,
                    'box': xyxy # [xmin, ymin, xmax, ymax]
                })

        processed_results = {
            'detections': detections_list,
            'count': len(detections_list)
        }
        
        # 4. Get the annotated image (YOLO's plot method)
        # result.plot() returns a numpy array (BGR format by default)
        annotated_np_array = result.plot()
        
        # Convert BGR (OpenCV format) to RGB (PIL format)
        annotated_pil_image = Image.fromarray(annotated_np_array[..., ::-1]) 
        
        return processed_results, annotated_pil_image