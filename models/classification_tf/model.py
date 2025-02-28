import os
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

IMAGE_SIZE = (256, 256)

def preprocess_image(img_path):
    img = load_img(img_path, target_size=IMAGE_SIZE)
    img = img_to_array(img) / 255.0
    return img

def load_segmentation_model():
    # Use MobileNetV2 as the base model
    base_model = tf.keras.applications.MobileNetV2(input_shape=(*IMAGE_SIZE, 3), include_top=False)
    base_model.trainable = False  # Freeze the base model
    
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = base_model(inputs, training=False)
    x = tf.keras.layers.Conv2D(256, 3, padding='same', activation='relu')(x)  # Convolutional layer for processing
    
    # Add transpose convolution layers to upscale the feature map to the original size
    x = tf.keras.layers.Conv2DTranspose(128, 3, strides=2, padding='same', activation='relu')(x)  # Upsample to 16x16
    x = tf.keras.layers.Conv2DTranspose(128, 3, strides=2, padding='same', activation='relu')(x)  # Upsample to 32x32
    x = tf.keras.layers.Conv2DTranspose(128, 3, strides=2, padding='same', activation='relu')(x)  # Upsample to 64x64
    x = tf.keras.layers.Conv2DTranspose(128, 3, strides=2, padding='same', activation='relu')(x)  # Upsample to 128x128
    x = tf.keras.layers.Conv2DTranspose(128, 3, strides=2, padding='same', activation='relu')(x)  # Upsample to 256x256
    
    # Add a final 1x1 convolution to predict the binary mask
    x = tf.keras.layers.Conv2D(1, 1, activation='sigmoid')(x)  # Output layer for segmentation mask
    
    model = tf.keras.Model(inputs, x)

    model.load_weights(os.path.join('models', 'classification_tf', 'saved_models', 'segmentation_model_weights.weights.h5'))
    return model

def load_road_type_model():
    base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(256, 256, 3))
    base_model.trainable = False  # Freeze base model layers
    
    model = tf.keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(3, activation='softmax')  # 3 classes: asphalt, paved, unpaved
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.load_weights(os.path.join('models', 'classification_tf', 'saved_models', 'Road_TYPE_best_model_road_type.weights.h5'))
    return model

def load_road_asphalt_condition():
    base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(256, 256, 3))
    base_model.trainable = False  # Freeze base model layers
    
    model = tf.keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(3, activation='softmax')  # 3 classes: bad, regular, good
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.load_weights(os.path.join('models', 'classification_tf', 'saved_models', 'model_Asphalt_weights.weights.h5'))
    return model

def load_road_paved_condition():
    base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(256, 256, 3))
    base_model.trainable = False  # Freeze base model layers
    
    model = tf.keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(3, activation='softmax')  # 3 classes: bad, regular, good
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.load_weights(os.path.join('models', 'classification_tf', 'saved_models', 'model_Paved_weights.weights.h5'), skip_mismatch=True)
    return model

def load_road_unpaved_condition():
    base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(256, 256, 3))
    base_model.trainable = False  # Freeze base model layers
    
    model = tf.keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(3, activation='softmax')  # 3 classes: bad, regular, good
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.load_weights(os.path.join('models', 'classification_tf', 'saved_models', 'model_Unpaved_weights.weights.h5'), skip_mismatch=True)
    return model