import os
import shutil
import numpy as np
from sklearn.model_selection import train_test_split
import random

# Set random seeds for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Define split ratios
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

def create_directory_structure():
    """Create necessary directories for the split dataset"""
    base_dirs = ['train', 'val', 'test']
    for base_dir in base_dirs:
        for disease_dir in os.listdir('dataset'):
            os.makedirs(os.path.join(base_dir, disease_dir), exist_ok=True)

def get_all_image_paths():
    """Get all image paths and their corresponding labels"""
    image_paths = []
    labels = []
    class_names = sorted(os.listdir('dataset'))
    
    for class_idx, class_name in enumerate(class_names):
        class_dir = os.path.join('dataset', class_name)
        if os.path.isdir(class_dir):
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append(os.path.join(class_dir, img_name))
                    labels.append(class_idx)
    
    return image_paths, labels, class_names

def split_dataset(image_paths, labels):
    """Split dataset into train, validation, and test sets"""
    # First split: 80% train, 20% temp (will be split into val and test)
    train_paths, temp_paths, train_labels, temp_labels = train_test_split(
        image_paths, labels,
        test_size=0.2,
        stratify=labels,
        random_state=RANDOM_SEED
    )
    
    # Second split: split temp into validation and test (50% each of the 20%)
    val_paths, test_paths, val_labels, test_labels = train_test_split(
        temp_paths, temp_labels,
        test_size=0.5,
        stratify=temp_labels,
        random_state=RANDOM_SEED
    )
    
    return {
        'train': (train_paths, train_labels),
        'val': (val_paths, val_labels),
        'test': (test_paths, test_labels)
    }

def copy_files(split_data, class_names):
    """Copy files to their respective directories"""
    for split_name, (paths, labels) in split_data.items():
        print(f"\nProcessing {split_name} set...")
        for img_path, label in zip(paths, labels):
            # Get the class name and image name
            class_name = class_names[label]
            img_name = os.path.basename(img_path)
            
            # Create destination path
            dest_path = os.path.join(split_name, class_name, img_name)
            
            # Copy the file
            shutil.copy2(img_path, dest_path)

def print_split_statistics(split_data, class_names):
    """Print statistics about the split dataset"""
    print("\nDataset Split Statistics:")
    print("-" * 50)
    
    for split_name, (paths, labels) in split_data.items():
        print(f"\n{split_name.capitalize()} Set:")
        total_images = len(paths)
        print(f"Total images: {total_images}")
        
        # Count images per class
        for class_idx, class_name in enumerate(class_names):
            class_count = sum(1 for l in labels if l == class_idx)
            percentage = (class_count / total_images) * 100
            print(f"{class_name}: {class_count} images ({percentage:.1f}%)")

def main():
    print("Starting dataset split process...")
    
    # Create directory structure
    print("Creating directory structure...")
    create_directory_structure()
    
    # Get all image paths and labels
    print("Collecting image paths and labels...")
    image_paths, labels, class_names = get_all_image_paths()
    
    # Split the dataset
    print("Splitting dataset...")
    split_data = split_dataset(image_paths, labels)
    
    # Copy files to their respective directories
    print("Copying files to new directories...")
    copy_files(split_data, class_names)
    
    # Print statistics
    print_split_statistics(split_data, class_names)
    
    print("\nDataset split completed successfully!")

if __name__ == "__main__":
    main() 