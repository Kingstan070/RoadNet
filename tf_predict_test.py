from models.classification_tf.predict import process_images

image_paths = [
    r"data/uploaded_files/frame_0000.jpg",
    r"data/uploaded_files/frame_4476.jpg",
    r"data/uploaded_files/frame_4625.jpg",
    r"data/uploaded_files/frame_4327.jpg",
    r"data/uploaded_files/frame_4476.jpg",
    r"data/uploaded_files/frame_4178.jpg",
]
process_images(image_paths)