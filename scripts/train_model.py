import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import json

# Set memory growth for GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU memory growth enabled")
    except RuntimeError as e:
        print(e)

# Constants
IMG_SIZE = 224
BATCH_SIZE = 64  # Increased batch size for GPU
EPOCHS = 50
LEARNING_RATE = 0.001
RANDOM_SEED = 42

# Define the number of classes
NUM_CLASSES = 13  # 3 potato + 10 tomato classes

def create_data_generators():
    """
    Create data generators for training, validation, and test sets
    """
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # For validation and test, only rescale
    val_test_datagen = ImageDataGenerator(rescale=1./255)

    # Create generators with prefetch for better GPU utilization
    train_generator = train_datagen.flow_from_directory(
        'train',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        seed=RANDOM_SEED
    )

    validation_generator = val_test_datagen.flow_from_directory(
        'val',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        seed=RANDOM_SEED,
        shuffle=False
    )

    test_generator = val_test_datagen.flow_from_directory(
        'test',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        seed=RANDOM_SEED,
        shuffle=False
    )

    # Enable prefetching for better GPU utilization
    train_generator = tf.data.Dataset.from_generator(
        lambda: train_generator,
        output_types=(tf.float32, tf.float32),
        output_shapes=([None, IMG_SIZE, IMG_SIZE, 3], [None, NUM_CLASSES])
    ).prefetch(tf.data.AUTOTUNE)

    validation_generator = tf.data.Dataset.from_generator(
        lambda: validation_generator,
        output_types=(tf.float32, tf.float32),
        output_shapes=([None, IMG_SIZE, IMG_SIZE, 3], [None, NUM_CLASSES])
    ).prefetch(tf.data.AUTOTUNE)

    test_generator = tf.data.Dataset.from_generator(
        lambda: test_generator,
        output_types=(tf.float32, tf.float32),
        output_shapes=([None, IMG_SIZE, IMG_SIZE, 3], [None, NUM_CLASSES])
    ).prefetch(tf.data.AUTOTUNE)

    return train_generator, validation_generator, test_generator

def create_model():
    """
    Create and compile the MobileNetV2 model
    """
    # Load the pre-trained MobileNetV2 model
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )

    # Freeze the base model layers
    base_model.trainable = False

    # Add custom layers on top
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)

    # Create the model
    model = Model(inputs=base_model.input, outputs=predictions)

    # Compile the model with mixed precision for better GPU performance
    policy = tf.keras.mixed_precision.Policy('mixed_float16')
    tf.keras.mixed_precision.set_global_policy(policy)

    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_model(model, train_generator, validation_generator):
    """
    Train the model with callbacks
    """
    # Create callbacks
    checkpoint = ModelCheckpoint(
        'models/best_model.keras',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )

    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )

    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=3,
        min_lr=0.00001
    )

    # Train the model
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        callbacks=[checkpoint, early_stopping, reduce_lr],
        workers=4,  # Use multiple workers for data loading
        use_multiprocessing=True
    )

    return history

def evaluate_model(model, test_generator, class_names):
    """
    Evaluate the model on the test set and generate reports
    """
    # Get predictions
    predictions = model.predict(test_generator)
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_generator.classes

    # Generate classification report
    print("\nClassification Report:")
    print("-" * 50)
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(12, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('models/confusion_matrix.png')
    plt.close()

def plot_training_history(history):
    """
    Plot training and validation metrics
    """
    plt.figure(figsize=(12, 4))

    # Plot accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    # Plot loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.savefig('models/training_history.png')
    plt.close()

def save_class_mapping(train_generator):
    """
    Save the class mapping to a JSON file
    """
    class_mapping = {v: k for k, v in train_generator.class_indices.items()}
    with open('models/class_mapping.json', 'w') as f:
        json.dump(class_mapping, f, indent=4)

def main():
    # Create necessary directories
    os.makedirs('models', exist_ok=True)

    # Create data generators
    print("Creating data generators...")
    train_generator, validation_generator, test_generator = create_data_generators()

    # Create and compile model
    print("Creating model...")
    model = create_model()

    # Train the model
    print("Starting model training...")
    history = train_model(model, train_generator, validation_generator)

    # Plot training history
    print("Plotting training history...")
    plot_training_history(history)

    # Save class mapping
    print("Saving class mapping...")
    save_class_mapping(train_generator)

    # Evaluate model on test set
    print("Evaluating model on test set...")
    evaluate_model(model, test_generator, list(train_generator.class_indices.keys()))

    # Save the final model
    print("Saving final model...")
    model.save('models/final_model.keras')

    print("Training completed successfully!")

if __name__ == "__main__":
    main() 