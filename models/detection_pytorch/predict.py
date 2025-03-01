import cv2
from ultralytics import YOLO
import os

def detect_objects(detection_requests):
    # Set the model path
    model_path = os.path.join("models", "detection_pytorch", "saved_models", "best_model.pt")
    
    # Load the YOLO model
    model = YOLO(model_path)

    all_detection_results = []

    for request in detection_requests:
        input_path = request["image_path"]
        x = request["x"]
        y = request["y"]
        width = request["width"]
        height = request["height"]

        # Load and crop the image
        image = cv2.imread(input_path)

        # Perform object detection on the cropped image
        results = model.predict(source=image, show=False)

        # Extract detection results
        detection_results = []
        for result in results:
            for box in result.boxes:
                detection_results.append({
                    "class": int(box.cls),
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()
                })
        
        all_detection_results.append({
            "image_path": input_path,
            "detection_results": detection_results
        })
    
    return all_detection_results