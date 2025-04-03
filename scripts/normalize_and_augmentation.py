import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Define paths
dataset_dir = "E:/crop disease detection/dataset"
target_size = (224, 224)  # Image size for MobileNetV2
batch_size = 32  # You can adjust batch size

# ✅ Define Data Augmentation and Normalization
train_datagen = ImageDataGenerator(
    rescale=1./255,  # Normalize pixel values to [0,1]
    rotation_range=30,  # Rotate images by up to 30 degrees
    width_shift_range=0.2,  # Shift width by 20%
    height_shift_range=0.2,  # Shift height by 20%
    shear_range=0.2,  # Apply shear transformations
    zoom_range=0.2,  # Random zooming
    horizontal_flip=True,  # Flip images horizontally
    fill_mode='nearest'  # Fill missing pixels after transformations
)

# ✅ Load the dataset
train_generator = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical'  # Multi-class classification
)

# Print class labels
print("Class labels:", train_generator.class_indices)
