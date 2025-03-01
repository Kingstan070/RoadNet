from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from models.detection_pytorch.predict import detect_objects

app = FastAPI()

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class ImageResult(BaseModel):
    image_path: str
    road_type: str
    road_condition: str
    bounding_box: BoundingBox

class DetectionRequests(BaseModel):
    results: List[ImageResult]

@app.post("/detect_potholes/")
async def detect_potholes(requests: DetectionRequests):
    # Check if all image files exist
    for result in requests.results:
        if not os.path.exists(result.image_path):
            raise HTTPException(status_code=400, detail=f"File not found: {result.image_path}")
    
    # Prepare detection requests
    detection_requests = []
    for result in requests.results:
        detection_requests.append({
            "image_path": result.image_path,
            "x": result.bounding_box.x,
            "y": result.bounding_box.y,
            "width": result.bounding_box.width,
            "height": result.bounding_box.height
        })
    
    # Perform object detection
    detection_results = detect_objects(detection_requests=detection_requests)
    
    # Combine the detection results with the original details
    combined_results = []
    for original_result, detection_result in zip(requests.results, detection_results):
        combined_result = {
            "image_path": original_result.image_path,
            "road_type": original_result.road_type,
            "road_condition": original_result.road_condition,
            "bounding_box": original_result.bounding_box.dict(),
            "detection_results": detection_result["detection_results"]
        }
        combined_results.append(combined_result)
    
    return {"results": combined_results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)