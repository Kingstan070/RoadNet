from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import os
from models.classification_tf.predict import process_images

app = FastAPI()

class ImagePaths(BaseModel):
    image_paths: List[str]

@app.post("/process_images/")
async def process_images_endpoint(image_paths: ImagePaths):
    # Check if all file paths exist
    for path in image_paths.image_paths:
        if not os.path.exists(path):
            raise HTTPException(status_code=400, detail=f"File not found: {path}")
    
    results_json = process_images(image_paths.image_paths)
    return {"results": results_json}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)