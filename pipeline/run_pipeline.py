import requests
import pandas as pd
import json

def call_tensorflow_api(image_paths):
    url = "http://localhost:8001/process_images/"
    payload = {"image_paths": image_paths}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["results"]

def call_pytorch_api(results):
    url = "http://localhost:8002/detect_potholes/"
    payload = {'results' : results}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["results"]

def convert_to_dataframe(results):
    data = []
    for result in results:
        detection_classes = []
        detection_confidences = []
        detection_bboxes = []
        for detection in result["detection_results"]:
            detection_classes.append(detection["class"])
            detection_confidences.append(detection["confidence"])
            detection_bboxes.append(detection["bbox"])
        
        pothole_data = json.dumps(result["detection_results"])
        
        data.append({
            "image_path": result["image_path"],
            "road_type": result["road_type"],
            "road_condition": result["road_condition"],
            "pothole_data": pothole_data
        })
    return pd.DataFrame(data)

def run_pipeline(image_paths):
    # Step 1: Call TensorFlow API
    tf_results = call_tensorflow_api(image_paths)
    
    # Step 2: Call PyTorch API
    combined_results = call_pytorch_api(tf_results)
    
    # Step 3: Convert to DataFrame
    df = convert_to_dataframe(combined_results)
    return df