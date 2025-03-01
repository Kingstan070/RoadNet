import cv2
import numpy as np
import json
from models.classification_tf.model import (
    preprocess_image,
    load_segmentation_model,
    load_road_type_model,
    load_road_asphalt_condition,
    load_road_paved_condition,
    load_road_unpaved_condition
)

# Load models
segmentation_model = load_segmentation_model()
road_type_model = load_road_type_model()
asphalt_condition_model = load_road_asphalt_condition()
paved_condition_model = load_road_paved_condition()
unpaved_condition_model = load_road_unpaved_condition()

def crop_segmented_area_and_bounding_box(original_image, mask, image_size=(256, 256)):
    # Threshold the mask to binary format (use the mask shape)
    binary_mask = (mask[0, ..., 0] > 0.5).astype(np.uint8)  # Shape: (256, 256)
    
    # Resize the binary mask to match the original image size
    binary_mask_resized = cv2.resize(binary_mask, (original_image.shape[1], original_image.shape[0]))

    # Find contours in the binary mask to get the segmented areas
    contours, _ = cv2.findContours(binary_mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No segmented area detected.")
        return None, None  # Return None if no contours are found
    
    # Find the bounding box surrounding the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Optionally, visualize the bounding box if needed:
    cv2.rectangle(original_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Now, crop the original image using the bounding box directly (without resizing)
    cropped_image = original_image[y:y+h, x:x+w]

    # Optionally, resize the cropped image to match the model's input size (e.g., 256x256)
    cropped_image_resized = cv2.resize(cropped_image, image_size)

    return cropped_image_resized, (x, y, w, h)

def segment_image(image_path):
    # Preprocess the image
    image = preprocess_image(image_path)
    if image is None:
        raise ValueError(f"Failed to preprocess image: {image_path}")
    
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    # Debugging: Print the shape and dtype of the image
    print(f"Image shape: {image.shape}, dtype: {image.dtype}")

    # Predict the segmentation mask
    mask = segmentation_model.predict(image)
    return image[0], mask

def classify_road_type(image):
    # Preprocess the image
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    # Predict the road type
    predictions = road_type_model.predict(image)
    road_type = np.argmax(predictions, axis=1)[0]
    road_type_labels = ["asphalt", "paved", "unpaved"]
    return road_type_labels[road_type]

def classify_road_condition(image, road_type):
    # Preprocess the image
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    # Predict the road condition based on the road type
    if road_type == "asphalt":
        predictions = asphalt_condition_model.predict(image)
    elif road_type == "paved":
        predictions = paved_condition_model.predict(image)
    else:
        predictions = unpaved_condition_model.predict(image)

    road_condition = np.argmax(predictions, axis=1)[0]
    road_condition_labels = ["bad", "regular", "good"] if road_type == "asphalt" else ["bad", "regular"]
    return road_condition_labels[road_condition]

def process_images(image_paths):
    results = []
    for image_path in image_paths:
        # Segment the image
        original_image, mask = segment_image(image_path)
        
        # Crop the segmented area and get bounding box
        cropped_image, bounding_box = crop_segmented_area_and_bounding_box(original_image, mask)
        
        if cropped_image is not None:
            # Classify the road type
            road_type = classify_road_type(cropped_image)
            
            # Classify the road condition based on the road type
            road_condition = classify_road_condition(cropped_image, road_type)
            
            # Append the result
            results.append({
                "image_path": image_path,
                "road_type": road_type,
                "road_condition": road_condition,
                "bounding_box": {
                    "x": bounding_box[0],
                    "y": bounding_box[1],
                    "width": bounding_box[2],
                    "height": bounding_box[3]
                }
            })
        else:
            results.append({
                "image_path": image_path,
                "error": "No segmented area detected"
            })
    
    return results